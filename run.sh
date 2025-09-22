cd Othello/test_code

# Default to both games
GAME_MODE="both"
LOG_TO_FILE=true
TIME_LIMIT=2

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
        --log-file)
            LOG_TO_FILE=true
            shift
            ;;
        --console)
            LOG_TO_FILE=false
            shift
            ;;
        --time)
            TIME_LIMIT="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [--white|--black|--both] [--log-file|--console] [--time SECONDS]"
            echo ""
            echo "Options:"
            echo "  --white    Run only as white player"
            echo "  --black    Run only as black player"
            echo "  --both     Run as both white and black (default)"
            echo "  --log-file Stream logs to files (default)"
            echo "  --console  Stream logs to console instead of files"
            echo "  --time     Time limit in seconds (default: 2)"
            echo "  -h, --help Show this help message"
            echo ""
            echo "Example: $0 --white --console --time 5"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use -h or --help for usage information"
            exit 1
            ;;
    esac
done

echo "Usage: othellostart white_player black_player time_limit"
echo "Game mode: $GAME_MODE"
echo "Time limit: $TIME_LIMIT seconds"

# Set player paths
OUR_AI="../othello.sh"
NAIVE_PLAYER="./othello_naive.sh"

# Run white game only if flag allows it
if [ "$GAME_MODE" = "white" ] || [ "$GAME_MODE" = "both" ]; then
    echo "=========================================="
    echo "Playing as WHITE (our AI vs naive black)"
    echo "=========================================="

    # Run game with our AI as white
    if [ "$LOG_TO_FILE" = true ]; then
        echo "Logging white game to white_game.log..."
        white_output=$(./othellostart.sh $OUR_AI $NAIVE_PLAYER $TIME_LIMIT 2>&1 | tee white_game.log)
    else
        white_output=$(./othellostart.sh $OUR_AI $NAIVE_PLAYER $TIME_LIMIT 2>&1)
        echo "$white_output"
    fi

    # Extract the last 6 lines from white game results
    white_results=$(echo "$white_output" | tail -6)

    # Check if our AI won as white
    white_won_check=$(echo "$white_results" | grep -c "White won" 2>/dev/null || echo "0")
    white_won_check=$(echo "$white_won_check" | tr -d '\n')

    echo ""
    echo "=========================================="
    if [ "$white_won_check" -gt 0 ]; then
        echo "✅ WHITE GAME: Our AI WON!"
    else
        echo "❌ WHITE GAME: Our AI LOST!"
    fi
    echo "=========================================="
else
    # Initialize empty results for white game when not running
    white_results=""
    white_won_check="0"
fi

# Run black game only if flag allows it
if [ "$GAME_MODE" = "black" ] || [ "$GAME_MODE" = "both" ]; then
    echo ""
    echo "=========================================="
    echo "Playing as BLACK - naive white vs our AI"
    echo "=========================================="

    # Run game with our AI as black
    if [ "$LOG_TO_FILE" = true ]; then
        echo "Logging black game to black_game.log..."
        black_output=$(./othellostart.sh $NAIVE_PLAYER $OUR_AI $TIME_LIMIT 2>&1 | tee black_game.log)
    else
        black_output=$(./othellostart.sh $NAIVE_PLAYER $OUR_AI $TIME_LIMIT 2>&1)
        echo "$black_output"
    fi

    # Extract the last 6 lines from black game results
    black_results=$(echo "$black_output" | tail -6)

    # Check if our AI won as black
    black_won_check=$(echo "$black_results" | grep -c "Black won" 2>/dev/null || echo "0")
    black_won_check=$(echo "$black_won_check" | tr -d '\n')

    echo ""
    echo "=========================================="
    if [ "$black_won_check" -gt 0 ]; then
        echo "✅ BLACK GAME: Our AI WON!"
    else
        echo "❌ BLACK GAME: Our AI LOST!"
    fi
    echo "=========================================="
else
    # Initialize empty results for black game when not running
    black_results=""
    black_won_check="0"
fi

# Display results only for games that were played
if [ "$GAME_MODE" = "white" ] || [ "$GAME_MODE" = "both" ]; then
    echo ""
    echo "=========================================="
    echo "WHITE GAME RESULTS (stored from above):"
    echo "=========================================="
    echo "$white_results"
fi

if [ "$GAME_MODE" = "black" ] || [ "$GAME_MODE" = "both" ]; then
    echo ""
    echo "=========================================="
    echo "BLACK GAME RESULTS (stored from above):"
    echo "=========================================="
    echo "$black_results"
fi

# Check if our AI won games and extract points
white_won=$(echo "$white_results" | grep -c "White won" 2>/dev/null || echo "0")
black_won=$(echo "$black_results" | grep -c "Black won" 2>/dev/null || echo "0")

# Remove any newlines and ensure we have clean integers
white_won=$(echo "$white_won" | tr -d '\n')
black_won=$(echo "$black_won" | tr -d '\n')

# Extract points from results
white_points=$(echo "$white_results" | grep -o "[0-9]* points" | head -1 | grep -o "[0-9]*" || echo "0")
black_points=$(echo "$black_results" | grep -o "[0-9]* points" | head -1 | grep -o "[0-9]*" || echo "0")

# Final summary based on game mode
echo ""
echo "=========================================="
if [ "$GAME_MODE" = "both" ]; then
    if [ "$white_won" -gt 0 ] && [ "$black_won" -gt 0 ]; then
        echo "🎉 PASSED: Our AI won both games! 🎉"
    else
        echo "❌ FAILED: Our AI did not win both games"
        
        if [ "$white_won" -gt 0 ]; then
            echo "✅ WON as WHITE with $white_points points"
        else
            echo "❌ LOST as WHITE (opponent won with $white_points points)"
        fi
        
        if [ "$black_won" -gt 0 ]; then
            echo "✅ WON as BLACK with $black_points points"
        else
            echo "❌ LOST as BLACK (opponent won with $black_points points)"
        fi
    fi
elif [ "$GAME_MODE" = "white" ]; then
    if [ "$white_won" -gt 0 ]; then
        echo "🎉 PASSED: Our AI won as WHITE! 🎉"
        echo "✅ WON as WHITE with $white_points points"
    else
        echo "❌ FAILED: Our AI lost as WHITE"
        echo "❌ LOST as WHITE (opponent won with $white_points points)"
    fi
elif [ "$GAME_MODE" = "black" ]; then
    if [ "$black_won" -gt 0 ]; then
        echo "🎉 PASSED: Our AI won as BLACK! 🎉"
        echo "✅ WON as BLACK with $black_points points"
    else
        echo "❌ FAILED: Our AI lost as BLACK"
        echo "❌ LOST as BLACK (opponent won with $black_points points)"
    fi
fi
echo "=========================================="

echo "=========================================="