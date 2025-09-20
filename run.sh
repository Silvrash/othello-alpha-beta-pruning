cd Othello/test_code

echo "Usage: othellostart white_player black_player time_limit"

# Set time limit in seconds
TIME_LIMIT=2

# Set player paths
OUR_AI="../othello_1.sh"
NAIVE_PLAYER="./othello_naive.sh"

echo "=========================================="
echo "Playing as WHITE (our AI vs naive black)"
echo "=========================================="

# Run game with our AI as white, capture output while displaying in real-time
white_output=$(./othellostart.sh $OUR_AI $NAIVE_PLAYER $TIME_LIMIT 2>&1 | tee /dev/tty)

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

echo ""
echo "=========================================="
echo "Playing as BLACK - naive white vs our AI"
echo "=========================================="

# Run game with our AI as black, display in real-time
black_output=$(./othellostart.sh $NAIVE_PLAYER $OUR_AI $TIME_LIMIT 2>&1 | tee /dev/tty)

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

echo ""
echo "=========================================="
echo "WHITE GAME RESULTS (stored from above):"
echo "=========================================="
echo "$white_results"
echo ""
echo "=========================================="
echo "BLACK GAME RESULTS (stored from above):"
echo "=========================================="
echo "$black_results"

# Check if our AI won both games and extract points
white_won=$(echo "$white_results" | grep -c "White won" 2>/dev/null || echo "0")
black_won=$(echo "$black_results" | grep -c "Black won" 2>/dev/null || echo "0")

# Remove any newlines and ensure we have clean integers
white_won=$(echo "$white_won" | tr -d '\n')
black_won=$(echo "$black_won" | tr -d '\n')

# Extract points from results
white_points=$(echo "$white_results" | grep -o "[0-9]* points" | head -1 | grep -o "[0-9]*" || echo "0")
black_points=$(echo "$black_results" | grep -o "[0-9]* points" | head -1 | grep -o "[0-9]*" || echo "0")

if [ "$white_won" -gt 0 ] && [ "$black_won" -gt 0 ]; then
    echo ""
    echo "=========================================="
    echo "🎉 PASSED: Our AI won both games! 🎉"
    echo "=========================================="
else
    echo ""
    echo "=========================================="
    echo "❌ FAILED: Our AI did not win both games"
    echo "=========================================="
    
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
    
    echo "=========================================="
fi

echo "=========================================="