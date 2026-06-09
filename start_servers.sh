#!/bin/bash
# Start both backend and frontend servers

echo "Starting Green Model Advisor servers..."
echo ""
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo ""

# Start backend in background
echo "Starting backend (Python FastAPI)..."
cd /c/games/green-model-advisor
source venv/Scripts/activate
python run.py &
BACKEND_PID=$!

sleep 3

# Start frontend in background
echo "Starting frontend (React Vite)..."
cd /c/games/green-model-advisor/client
npm run dev &
FRONTEND_PID=$!

sleep 2

echo ""
echo "Both servers started!"
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for Ctrl+C
wait

# Cleanup
kill $BACKEND_PID 2>/dev/null
kill $FRONTEND_PID 2>/dev/null
