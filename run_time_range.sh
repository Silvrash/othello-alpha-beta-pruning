#!/bin/bash

# Time Range Testing Script for Othello AI
# This script runs the main run.sh script with different time limits from 1 to 10 seconds
# and logs all results to files for analysis

cd "$(dirname "$0")"

# Default to both games
GAME_MODE="both"

# Time limits to test
TIME_LIMITS=(0.5 1 2 3 4 5 6 7 8 9 10)

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --white)
            GAME_MODE="white"
            shift
            ;;
        --black)
            GAME_MODE="black"
            shift
            ;;
        --both)
            GAME_MODE="both"
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [--white|--black|--both]"
            echo ""
            echo "Options:"
            echo "  --white    Run only as white player"
            echo "  --black    Run only as black player"
            echo "  --both     Run as both white and black (default)"
            echo "  -h, --help Show this help message"
            echo ""
            echo "This script runs games from 1 to 10 seconds and logs all results to files."
            echo "Example: $0 --white"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use -h or --help for usage information"
            exit 1
            ;;
    esac
done

echo "=========================================="
echo "🕐 TIME RANGE TESTING (1-10 seconds)"
echo "=========================================="
echo "Game mode: $GAME_MODE"
echo "All logs will be saved to files"
echo ""

# Create logs directory if it doesn't exist and clean existing logs
mkdir -p time_range_logs
echo "Cleaning existing log files..."
rm -f time_range_logs/*.log

# Initialize arrays to store results
declare -a white_wins_by_time
declare -a black_wins_by_time
declare -a white_points_by_time
declare -a black_points_by_time
declare -a time_limits

# Function to cleanup background jobs on exit
cleanup() {
    echo ""
    echo "🛑 Interrupted! Cleaning up background processes..."
    # Kill all background jobs
    jobs -p | xargs -r kill
    # Clean up any temporary result files
    rm -f time_range_logs/*.result
    echo "✅ Cleanup completed"
    exit 1
}

# Set up signal handlers for cleanup
trap cleanup SIGINT SIGTERM

# Function to run a single game
run_single_game() {
    local current_time=$1
    local game_type=$2
    local log_file=$3
    
    {
        echo "Playing as $game_type (our AI vs naive opponent) - Time: ${current_time}s"
        echo "Logging to: $log_file"
        
        # Run game with our AI using run.sh with time parameter
        temp_output=$(./run.sh --$game_type --console --time $current_time 2>&1)
        
        # Extract results from the game output - look for the most recent game results
        # Search for the last occurrence of "won with X points" in the output
        last_white_result=$(echo "$temp_output" | grep "White won with" | tail -1)
        last_black_result=$(echo "$temp_output" | grep "Black won with" | tail -1)
        
        # Determine if our AI won based on which color it was playing
        if [ "$game_type" = "white" ]; then
            # Our AI played as white, so it won if "White won" appears in the last result
            if [ -n "$last_white_result" ]; then
                won_check="1"
            else
                won_check="0"
            fi
        else
            # Our AI played as black, so it won if "Black won" appears in the last result
            if [ -n "$last_black_result" ]; then
                won_check="1"
            else
                won_check="0"
            fi
        fi
        
        won_check=$(echo "$won_check" | tr -d '\n')
        
        # Extract points from the appropriate result
        if [ "$game_type" = "white" ] && [ -n "$last_white_result" ]; then
            points=$(echo "$last_white_result" | grep -o "[0-9]* points" | grep -o "[0-9]*" || echo "0")
        elif [ "$game_type" = "black" ] && [ -n "$last_black_result" ]; then
            points=$(echo "$last_black_result" | grep -o "[0-9]* points" | grep -o "[0-9]*" || echo "0")
        else
            points="0"
        fi
        
        # Capitalize first letter of game_type for display
        if [ "$game_type" = "white" ]; then
            display_type="White"
        else
            display_type="Black"
        fi
        
        echo "$display_type game result: $won_check wins, $points points"
        
        # Write results to a temporary file for collection
        echo "$current_time,$game_type,$won_check,$points" > "${log_file}.result"
        
        # Write full game output to log file (including board)
        echo "$temp_output" >> "$log_file"
    } | tee -a "$log_file"
}

# Run games for each time limit in parallel
echo ""
echo "🚀 RUNNING ALL GAMES IN PARALLEL..."
echo "=========================================="

# Start all white games in background
if [ "$GAME_MODE" = "white" ] || [ "$GAME_MODE" = "both" ]; then
    for current_time in "${TIME_LIMITS[@]}"; do
        white_log="time_range_logs/${current_time}s_white_game.log"
        run_single_game $current_time "white" "$white_log" &
    done
fi

# Start all black games in background
if [ "$GAME_MODE" = "black" ] || [ "$GAME_MODE" = "both" ]; then
    for current_time in "${TIME_LIMITS[@]}"; do
        black_log="time_range_logs/${current_time}s_black_game.log"
        run_single_game $current_time "black" "$black_log" &
    done
fi

# Wait for all background jobs to complete
echo "⏳ Waiting for all games to complete..."
wait
echo "✅ All games completed!"

# Collect results from temporary files
echo ""
echo "📊 Collecting results..."
for current_time in "${TIME_LIMITS[@]}"; do
    time_limits+=($current_time)
    
    # Initialize default values
    white_won_check="0"
    white_points="0"
    black_won_check="0"
    black_points="0"
    
    # Read white results if available
    if [ "$GAME_MODE" = "white" ] || [ "$GAME_MODE" = "both" ]; then
        white_result_file="time_range_logs/${current_time}s_white_game.log.result"
        if [ -f "$white_result_file" ]; then
            IFS=',' read -r time game_type won_check points < "$white_result_file"
            white_won_check="$won_check"
            white_points="$points"
            rm "$white_result_file"  # Clean up temp file
        fi
    fi
    
    # Read black results if available
    if [ "$GAME_MODE" = "black" ] || [ "$GAME_MODE" = "both" ]; then
        black_result_file="time_range_logs/${current_time}s_black_game.log.result"
        if [ -f "$black_result_file" ]; then
            IFS=',' read -r time game_type won_check points < "$black_result_file"
            black_won_check="$won_check"
            black_points="$points"
            rm "$black_result_file"  # Clean up temp file
        fi
    fi
    
    # Store results
    white_wins_by_time+=($white_won_check)
    white_points_by_time+=($white_points)
    black_wins_by_time+=($black_won_check)
    black_points_by_time+=($black_points)
done

echo ""
echo "=========================================="
echo "📊 TIME RANGE ANALYSIS RESULTS"
echo "=========================================="

# Display time range results table
echo "Time | White | Black | White Points | Black Points"
echo "-----|-------|-------|--------------|-------------"

for i in "${!time_limits[@]}"; do
    time_limit="${time_limits[$i]}"
    white_result="${white_wins_by_time[$i]}"
    black_result="${black_wins_by_time[$i]}"
    white_pts="${white_points_by_time[$i]}"
    black_pts="${black_points_by_time[$i]}"
    
    if [ "$white_result" -gt 0 ]; then
        white_status="WIN"
    else
        white_status="LOSS"
    fi
    
    if [ "$black_result" -gt 0 ]; then
        black_status="WIN"
    else
        black_status="LOSS"
    fi
    
    printf "%4ds | %-4s | %-4s | %11s | %12s\n" "$time_limit" "$white_status" "$black_status" "$white_pts" "$black_pts"
done

echo ""
echo "📈 SUMMARY STATISTICS:"

# Calculate win rates
total_games=${#time_limits[@]}
white_wins=0
black_wins=0

for i in "${!white_wins_by_time[@]}"; do
    if [ "${white_wins_by_time[$i]}" -gt 0 ]; then
        white_wins=$((white_wins + 1))
    fi
    if [ "${black_wins_by_time[$i]}" -gt 0 ]; then
        black_wins=$((black_wins + 1))
    fi
done

white_win_rate=$((white_wins * 100 / total_games))
black_win_rate=$((black_wins * 100 / total_games))

echo "White Win Rate: $white_wins/$total_games ($white_win_rate%)"
echo "Black Win Rate: $black_wins/$total_games ($black_win_rate%)"

# Find best performing time
best_white_time=1
best_black_time=1
best_white_points=0
best_black_points=0

for i in "${!time_limits[@]}"; do
    if [ "${white_points_by_time[$i]}" -gt "$best_white_points" ]; then
        best_white_points="${white_points_by_time[$i]}"
        best_white_time="${time_limits[$i]}"
    fi
    if [ "${black_points_by_time[$i]}" -gt "$best_black_points" ]; then
        best_black_points="${black_points_by_time[$i]}"
        best_black_time="${time_limits[$i]}"
    fi
done

echo "Best White Performance: ${best_white_points} points at ${best_white_time}s"
echo "Best Black Performance: ${best_black_points} points at ${best_black_time}s"

echo ""
echo "📁 LOG FILES SAVED IN: time_range_logs/"
echo "   - Xs_white_game.log (for each time limit X)"
echo "   - Xs_black_game.log (for each time limit X)"
echo "=========================================="

# Cleanup function for normal exit
cleanup_normal() {
    # Clean up any remaining temporary result files
    rm -f time_range_logs/*.result
}

# Set up cleanup for normal exit
trap cleanup_normal EXIT
