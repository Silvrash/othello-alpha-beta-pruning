#!/bin/bash
# Script to run our AI against the naive player for given time limits
# Usage: ./run.sh [--white] [--black] [--time time_limit1,time_limit2,...] [--time time_limit3] ...
# Options:
#   --white: Run only with AI as white (naive as black)
#   --black: Run only with AI as black (naive as white)  
#   --time: Specify time limits (comma-separated or multiple flags)
#   Default: Run both configurations with 10-second time limit

cd Othello/test_code
# Configuration
OUR_AI="../Python/othello.sh"
NAIVE_PLAYER="./othello_naive.sh"

# Parse arguments
RUN_WHITE=false
RUN_BLACK=false
TIME_LIMITS=()
EXPECTING_TIME=false

# Default behavior: run both if no flags specified
if [ $# -eq 0 ]; then
    RUN_WHITE=true
    RUN_BLACK=true
    TIME_LIMITS=(10)
fi

# Function to add time limits (handles comma-separated values)
add_time_limits() {
    local time_input="$1"
    # Split by comma and add each time limit
    IFS=',' read -ra TIMES <<< "$time_input"
    for time in "${TIMES[@]}"; do
        # Trim whitespace and validate
        time=$(echo "$time" | xargs)
        # Check if it's a valid positive number (integer or decimal)
        if [[ $time =~ ^[0-9]+(\.[0-9]+)?$ ]] && [[ $(echo "$time > 0" | awk '{print ($1 > 0)}') == "1" ]]; then
            TIME_LIMITS+=($time)
        else
            echo "Error: Invalid time limit '$time'. Must be a positive number (integers or decimals allowed)."
            echo "Usage: ./run.sh [--white] [--black] [--time time_limit1,time_limit2,...] [--time time_limit3] ..."
            exit 1
        fi
    done
}

# Parse command line arguments
for arg in "$@"; do
    if [ "$EXPECTING_TIME" = true ]; then
        add_time_limits "$arg"
        EXPECTING_TIME=false
    else
        case $arg in
            --white)
                RUN_WHITE=true
                ;;
            --black)
                RUN_BLACK=true
                ;;
            --time)
                EXPECTING_TIME=true
                ;;
            *)
                echo "Unknown argument: $arg"
                echo "Usage: ./run.sh [--white] [--black] [--time time_limit1,time_limit2,...] [--time time_limit3] ..."
                exit 1
                ;;
        esac
    fi
done

# Check if we were expecting a time value but didn't get one
if [ "$EXPECTING_TIME" = true ]; then
    echo "Error: --time flag requires a time limit value"
    echo "Usage: ./run.sh [--white] [--black] [--time time_limit1,time_limit2,...] [--time time_limit3] ..."
    exit 1
fi

# If no time limits specified, use default
if [ ${#TIME_LIMITS[@]} -eq 0 ]; then
    TIME_LIMITS=(10)
fi

# If no flags specified but time limits given, run both
if [ "$RUN_WHITE" = false ] && [ "$RUN_BLACK" = false ]; then
    RUN_WHITE=true
    RUN_BLACK=true
fi

# Check if the AI script exists
if [ ! -f "$OUR_AI" ]; then
    echo "Error: AI script not found at $OUR_AI"
    echo "Please make sure the Python othello.sh script exists in the correct location"
    exit 1
fi

# Check if the naive player script exists
if [ ! -f "$NAIVE_PLAYER" ]; then
    echo "Error: Naive player script not found at $NAIVE_PLAYER"
    echo "Please make sure othello_naive.sh exists in the current directory"
    exit 1
fi

# Make sure the scripts are executable
chmod +x "$OUR_AI" 2>/dev/null
chmod +x "$NAIVE_PLAYER" 2>/dev/null

# Function to run a single game
run_game() {
    local white_player="$1"
    local black_player="$2"
    local time_limit="$3"
    local game_description="$4"
    local log_file="$5"
    
    echo "=========================================="
    echo "$game_description"
    echo "Time limit: $time_limit seconds per move"
    echo "White Player: $white_player"
    echo "Black Player: $black_player"
    echo "Log file: $log_file"
    echo "=========================================="
    echo ""
    
    # Run the game and capture output to log file
    # If multiple time limits, suppress console output but still log to file
    if [ ${#TIME_LIMITS[@]} -gt 1 ]; then
        ./othellostart.sh "$white_player" "$black_player" "$time_limit" > "$log_file" 2>&1
    else
        ./othellostart.sh "$white_player" "$black_player" "$time_limit" 2>&1 | tee "$log_file"
    fi
    
    # Extract winner information from the log
    local winner=$(grep "won with" "$log_file" | tail -1)
    local ai_color="$6"  # Pass AI color as 6th parameter
    
    # Extract winner's score
    local winner_score=$(echo "$winner" | grep -o '[0-9]\+ points' | grep -o '[0-9]\+')
    # Note: We can't determine the opponent's score from the current log format
    # The log only shows the winner's score, not both scores
    local opponent_score="unknown"
    
    echo ""
    echo "Game completed! $winner"
    echo ""
    
    # Return the winner info, AI color, winner score, and opponent score for later processing
    echo "$winner|$ai_color|$winner_score|$opponent_score"
}

# Create logs directory and reset it if it exists
if [ -d "../logs" ]; then
    echo "Clearing existing logs directory..."
    rm -rf ../logs/*
else
    echo "Creating logs directory..."
fi
mkdir -p ../logs

# Arrays to store results for summary
RESULTS=()

# Run games for each time limit
for time_limit in "${TIME_LIMITS[@]}"; do
    echo "Running games for time limit: ${time_limit}s"
    echo "=========================================="
    
    white_result=""
    black_result=""
    
    # Run games concurrently
    if [ "$RUN_WHITE" = true ] && [ "$RUN_BLACK" = true ]; then
        # Run both games in background
        log_file_white="../logs/${time_limit}s_white.log"
        log_file_black="../logs/${time_limit}s_black.log"
        
        echo "Starting both games concurrently..."
        
        # Start white game in background
        ./othellostart.sh "$OUR_AI" "$NAIVE_PLAYER" "$time_limit" > "$log_file_white" 2>&1 &
        white_pid=$!
        
        # Start black game in background
        ./othellostart.sh "$NAIVE_PLAYER" "$OUR_AI" "$time_limit" > "$log_file_black" 2>&1 &
        black_pid=$!
        
        # Wait for both games to complete
        wait $white_pid
        wait $black_pid
        
        # Wait a moment for log files to be written
        sleep 1
        
        # Get results from log files (with error handling)
        white_winner=""
        black_winner=""
        if [ -f "$log_file_white" ]; then
            white_winner="$(grep "won with" "$log_file_white" | tail -1)"
        fi
        if [ -f "$log_file_black" ]; then
            black_winner="$(grep "won with" "$log_file_black" | tail -1)"
        fi
        
        # Extract scores (with error handling)
        white_winner_score=0
        white_opponent_score=0
        black_winner_score=0
        black_opponent_score=0
        
        if [ -n "$white_winner" ]; then
            white_winner_score=$(echo "$white_winner" | grep -o '[0-9]\+ points' | grep -o '[0-9]\+')
            if [ -n "$white_winner_score" ]; then
                white_opponent_score="unknown"
            fi
        fi
        
        if [ -n "$black_winner" ]; then
            black_winner_score=$(echo "$black_winner" | grep -o '[0-9]\+ points' | grep -o '[0-9]\+')
            if [ -n "$black_winner_score" ]; then
                black_opponent_score="unknown"
            fi
        fi
        
        white_result="${white_winner}|white|${white_winner_score}|${white_opponent_score}"
        black_result="${black_winner}|black|${black_winner_score}|${black_opponent_score}"
        
        RESULTS+=("AI as White (${time_limit}s): ${white_result%%|*}")
        RESULTS+=("AI as Black (${time_limit}s): ${black_result%%|*}")
        
    elif [ "$RUN_WHITE" = true ]; then
        # Run only white game
        log_file="../logs/${time_limit}s_white.log"
        result=$(run_game "$OUR_AI" "$NAIVE_PLAYER" "$time_limit" "AI vs Naive Player (AI as White)" "$log_file" "white")
        white_result="$result"
        RESULTS+=("AI as White (${time_limit}s): ${result%%|*}")
        
    elif [ "$RUN_BLACK" = true ]; then
        # Run only black game
        log_file="../logs/${time_limit}s_black.log"
        result=$(run_game "$NAIVE_PLAYER" "$OUR_AI" "$time_limit" "AI vs Naive Player (AI as Black)" "$log_file" "black")
        black_result="$result"
        RESULTS+=("AI as Black (${time_limit}s): ${result%%|*}")
    fi
    
    # Show win/loss results after both games are completed
    echo "=========================================="
    echo "RESULTS FOR ${time_limit}s TIME LIMIT:"
    echo "=========================================="
    
    if [ "$RUN_WHITE" = true ] && [ -n "$white_result" ]; then
        IFS='|' read -r winner ai_color winner_score opponent_score <<< "$white_result"
        if [[ "$winner" == *"White won"* ]] && [[ "$ai_color" == "white" ]]; then
            echo "🎉 WE WON! (Playing as White) - Our Score: $winner_score"
        elif [[ "$winner" == *"Black won"* ]] && [[ "$ai_color" == "white" ]]; then
            echo "❌ WE LOST! (Playing as White, Black won) - Black's Score: $winner_score"
        fi
    fi
    
    if [ "$RUN_BLACK" = true ] && [ -n "$black_result" ]; then
        IFS='|' read -r winner ai_color winner_score opponent_score <<< "$black_result"
        if [[ "$winner" == *"Black won"* ]] && [[ "$ai_color" == "black" ]]; then
            echo "🎉 WE WON! (Playing as Black) - Our Score: $winner_score"
        elif [[ "$winner" == *"White won"* ]] && [[ "$ai_color" == "black" ]]; then
            echo "❌ WE LOST! (Playing as Black, White won) - White's Score: $winner_score"
        fi
    fi
    
    echo "Completed all games for time limit: ${time_limit}s"
    echo ""
done

# Create comprehensive analysis log file
ANALYSIS_LOG="../logs/comprehensive_analysis_$(date +%Y%m%d_%H%M%S).log"

echo "=========================================="
echo "COMPREHENSIVE ANALYSIS RESULTS"
echo "=========================================="

# Start logging to analysis file
{
    echo "=========================================="
    echo "COMPREHENSIVE ANALYSIS RESULTS"
    echo "=========================================="
    echo "Analysis generated on: $(date)"
    echo "Time limits tested: ${TIME_LIMITS[*]}"
    echo "Configurations run:"
    if [ "$RUN_WHITE" = true ]; then
        echo "  - AI as White vs Naive Player"
    fi
    if [ "$RUN_BLACK" = true ]; then
        echo "  - AI as Black vs Naive Player"
    fi
    echo ""
} | tee "$ANALYSIS_LOG"

# Initialize counters
white_wins=0
black_wins=0
white_total_games=0
black_total_games=0
white_points=()
black_points=()
best_white_points=0
best_black_points=0
best_white_time=""
best_black_time=""

# Initialize depth tracking arrays
white_depths=()
black_depths=()

# Function to extract depth information from log files
extract_depths_from_log() {
    local log_file="$1"
    local depths=()
    
    if [ -f "$log_file" ]; then
        # Extract all depth values from the log file
        while IFS= read -r line; do
            if [[ "$line" =~ "Depth reached: "([0-9]+) ]]; then
                depths+=(${BASH_REMATCH[1]})
            fi
        done < "$log_file"
    fi
    
    # Return depths as space-separated string
    echo "${depths[*]}"
}

# Function to extract mobility phase depth information from log files (moves 10-40)
extract_mobility_depths_from_log() {
    local log_file="$1"
    local depths=()
    local move_count=0
    
    if [ -f "$log_file" ]; then
        # Split content by "to move" to identify moves
        local content=$(cat "$log_file")
        local moves=($(echo "$content" | grep -n "to move" | cut -d: -f1))
        
        # Process each move section
        for i in "${!moves[@]}"; do
            move_count=$((move_count + 1))
            
            # Only process moves in the mobility phase (10-40)
            if [ $move_count -ge 10 ] && [ $move_count -le 40 ]; then
                # Get the line number for this move
                local line_num=${moves[$i]}
                
                # Look for depth information in the next few lines after this move
                local depth_line=$(sed -n "${line_num},$((line_num + 10))p" "$log_file" | grep "Depth reached:" | head -1)
                if [[ "$depth_line" =~ "Depth reached: "([0-9]+) ]]; then
                    local depth=${BASH_REMATCH[1]}
                    # Only include depths from 1 to 10 (matching calculate_average_depth logic)
                    if [ "$depth" -ge 1 ] && [ "$depth" -le 10 ]; then
                        depths+=($depth)
                    fi
                fi
            fi
        done
    fi
    
    # Return depths as space-separated string
    echo "${depths[*]}"
}

# Function to calculate average depth (only depths 1-10)
calculate_average_depth() {
    local depths=("$@")
    local sum=0
    local count=0
    
    for depth in "${depths[@]}"; do
        # Only include depths from 1 to 10
        if [ "$depth" -ge 1 ] && [ "$depth" -le 10 ]; then
            sum=$((sum + depth))
            count=$((count + 1))
        fi
    done
    
    if [ $count -eq 0 ]; then
        echo "0"
        return
    fi
    
    # Calculate average
    echo $((sum / count))
}

# Process results and extract depth information
for result in "${RESULTS[@]}"; do
    if [[ "$result" == *"AI as White"* ]]; then
        white_total_games=$((white_total_games + 1))
        if [[ "$result" == *"White won"* ]]; then
            white_wins=$((white_wins + 1))
            # Extract points
            points=$(echo "$result" | grep -o '[0-9]\+ points' | grep -o '[0-9]\+')
            white_points+=($points)
            if [ "$points" -gt "$best_white_points" ]; then
                best_white_points=$points
                best_white_time=$(echo "$result" | grep -o '[0-9]\+s')
            fi
        fi
    elif [[ "$result" == *"AI as Black"* ]]; then
        black_total_games=$((black_total_games + 1))
        if [[ "$result" == *"Black won"* ]]; then
            black_wins=$((black_wins + 1))
            # Extract points
            points=$(echo "$result" | grep -o '[0-9]\+ points' | grep -o '[0-9]\+')
            black_points+=($points)
            if [ "$points" -gt "$best_black_points" ]; then
                best_black_points=$points
                best_black_time=$(echo "$result" | grep -o '[0-9]\+s')
            fi
        fi
    fi
done

# Extract depth information from all log files
for time_limit in "${TIME_LIMITS[@]}"; do
    # Extract depths from white log files
    if [ "$RUN_WHITE" = true ]; then
        white_log="../logs/${time_limit}s_white.log"
        if [ -f "$white_log" ]; then
            depths_string=$(extract_depths_from_log "$white_log")
            if [ -n "$depths_string" ]; then
                read -ra depths_array <<< "$depths_string"
                white_depths+=("${depths_array[@]}")
            fi
        fi
    fi
    
    # Extract depths from black log files
    if [ "$RUN_BLACK" = true ]; then
        black_log="../logs/${time_limit}s_black.log"
        if [ -f "$black_log" ]; then
            depths_string=$(extract_depths_from_log "$black_log")
            if [ -n "$depths_string" ]; then
                read -ra depths_array <<< "$depths_string"
                black_depths+=("${depths_array[@]}")
            fi
        fi
    fi
done

# Calculate average depths
white_avg_depth=$(calculate_average_depth "${white_depths[@]}")
black_avg_depth=$(calculate_average_depth "${black_depths[@]}")

# Calculate win rates
if [ $white_total_games -gt 0 ]; then
    white_win_rate="$white_wins/$white_total_games"
    white_percentage=$((white_wins * 100 / white_total_games))
else
    white_win_rate="0/0"
    white_percentage=0
fi

if [ $black_total_games -gt 0 ]; then
    black_win_rate="$black_wins/$black_total_games"
    black_percentage=$((black_wins * 100 / black_total_games))
else
    black_win_rate="0/0"
    black_percentage=0
fi

# Display depth analysis table
{
    echo ""
    echo "📊 DEPTH ANALYSIS TABLE"
    echo "════════════════════════════════════════════════════════════"
    echo "┌─────────┬─────────────┬─────────────────────────┬─────────────────────┬─────────────────┬─────────────┐"
    echo "│ Color   │ Time limit  │ Result                  │ Avg Depth (10-40)   │ Moves (10-40)   │ Depth Range │"
    echo "├─────────┼─────────────┼─────────────────────────┼─────────────────────┼─────────────────┼─────────────┤"
} | tee -a "$ANALYSIS_LOG"

# Generate depth analysis table rows
for time_limit in "${TIME_LIMITS[@]}"; do
    # Process White results
    if [ "$RUN_WHITE" = true ]; then
        white_result=""
        white_mobility_depth=""
        white_mobility_moves=""
        white_depth_range=""
        
        # Find white result for this time limit
        for result in "${RESULTS[@]}"; do
            if [[ "$result" == *"AI as White"* ]] && [[ "$result" == *"${time_limit}s"* ]]; then
                if [[ "$result" == *"White won"* ]]; then
                    white_result="White won with $(echo "$result" | grep -o '[0-9]\+ points' | grep -o '[0-9]\+')"
                else
                    white_result="Black won with $(echo "$result" | grep -o '[0-9]\+ points' | grep -o '[0-9]\+')"
                fi
                break
            fi
        done
        
        # Calculate white mobility phase depth for this time limit
        white_log="../logs/${time_limit}s_white.log"
        if [ -f "$white_log" ]; then
            mobility_depths_string=$(extract_mobility_depths_from_log "$white_log")
            if [ -n "$mobility_depths_string" ]; then
                read -ra mobility_depths_array <<< "$mobility_depths_string"
                white_mobility_depth=$(calculate_average_depth "${mobility_depths_array[@]}")
                white_mobility_moves=${#mobility_depths_array[@]}
                
                # Calculate depth range
                if [ ${#mobility_depths_array[@]} -gt 0 ]; then
                    min_depth=${mobility_depths_array[0]}
                    max_depth=${mobility_depths_array[0]}
                    for depth in "${mobility_depths_array[@]}"; do
                        if [ "$depth" -lt "$min_depth" ]; then
                            min_depth=$depth
                        fi
                        if [ "$depth" -gt "$max_depth" ]; then
                            max_depth=$depth
                        fi
                    done
                    white_depth_range="${min_depth}-${max_depth}"
                else
                    white_depth_range="N/A"
                fi
            else
                white_mobility_depth="0"
                white_mobility_moves="0"
                white_depth_range="N/A"
            fi
        fi
        
        printf "│ %-7s │ %-11s │ %-23s │ %-19s │ %-15s │ %-11s │\n" "White" "${time_limit}s" "$white_result" "$white_mobility_depth" "$white_mobility_moves" "$white_depth_range"
    fi
    
    # Process Black results
    if [ "$RUN_BLACK" = true ]; then
        black_result=""
        black_mobility_depth=""
        black_mobility_moves=""
        black_depth_range=""
        
        # Find black result for this time limit
        for result in "${RESULTS[@]}"; do
            if [[ "$result" == *"AI as Black"* ]] && [[ "$result" == *"${time_limit}s"* ]]; then
                if [[ "$result" == *"Black won"* ]]; then
                    black_result="Black won with $(echo "$result" | grep -o '[0-9]\+ points' | grep -o '[0-9]\+')"
                else
                    black_result="White won with $(echo "$result" | grep -o '[0-9]\+ points' | grep -o '[0-9]\+')"
                fi
                break
            fi
        done
        
        # Calculate black mobility phase depth for this time limit
        black_log="../logs/${time_limit}s_black.log"
        if [ -f "$black_log" ]; then
            mobility_depths_string=$(extract_mobility_depths_from_log "$black_log")
            if [ -n "$mobility_depths_string" ]; then
                read -ra mobility_depths_array <<< "$mobility_depths_string"
                black_mobility_depth=$(calculate_average_depth "${mobility_depths_array[@]}")
                black_mobility_moves=${#mobility_depths_array[@]}
                
                # Calculate depth range
                if [ ${#mobility_depths_array[@]} -gt 0 ]; then
                    min_depth=${mobility_depths_array[0]}
                    max_depth=${mobility_depths_array[0]}
                    for depth in "${mobility_depths_array[@]}"; do
                        if [ "$depth" -lt "$min_depth" ]; then
                            min_depth=$depth
                        fi
                        if [ "$depth" -gt "$max_depth" ]; then
                            max_depth=$depth
                        fi
                    done
                    black_depth_range="${min_depth}-${max_depth}"
                else
                    black_depth_range="N/A"
                fi
            else
                black_mobility_depth="0"
                black_mobility_moves="0"
                black_depth_range="N/A"
            fi
        fi
        
        printf "│ %-7s │ %-11s │ %-23s │ %-19s │ %-15s │ %-11s │\n" "Black" "${time_limit}s" "$black_result" "$black_mobility_depth" "$black_mobility_moves" "$black_depth_range"
    fi
done

{
    echo "└─────────┴─────────────┴─────────────────────────┴─────────────────────┴─────────────────┴─────────────┘"
} | tee -a "$ANALYSIS_LOG"

{
    echo ""
    echo "SUMMARY STATISTICS"
    echo "════════════════════════════════════════════════════════════"
    echo "White Win Rate: $white_win_rate ($white_percentage%)"
    echo "Black Win Rate: $black_win_rate ($black_percentage%)"
    echo "White Average Depth: $white_avg_depth"
    echo "Black Average Depth: $black_avg_depth"

    if [ $best_white_points -gt 0 ]; then
        echo "Best White Performance: $best_white_points points at $best_white_time"
    fi

    if [ $best_black_points -gt 0 ]; then
        echo "Best Black Performance: $best_black_points points at $best_black_time"
    fi

    echo ""
    echo "LOG FILES SAVED IN: ../logs/"
    echo "════════════════════════════════════════════════════════════"
    echo ""
    echo "DETAILED GAME RESULTS:"
    echo "════════════════════════════════════════════════════════════"
    for result in "${RESULTS[@]}"; do
        echo "$result"
    done
    echo ""
    echo "Analysis completed at: $(date)"
} | tee -a "$ANALYSIS_LOG"

echo ""
echo "COMPREHENSIVE ANALYSIS SAVED TO: $ANALYSIS_LOG"
echo "════════════════════════════════════════════════════════════"
