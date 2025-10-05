# Agent Integration Documentation

## Overview

This document describes the integration of the new AI agent system with the frontend application. The integration allows users to create personalized learning goals using advanced AI-powered course generation and adaptive learning features.

## Architecture

### Backend Components

1. **Agent Routes** (`backend/app/routes/agents.py`)
   - RESTful API endpoints for agent interactions
   - Course creation and management
   - Learning plan generation
   - Progress tracking

2. **Tutoring System** (`new_agent/tutoring_system.py`)
   - Multi-agent AI tutoring system
   - Adaptive learning workflows
   - Progress tracking and analytics

3. **Dynamic Learning Planner** (`new_agent/dynamic_learning_planner.py`)
   - Real-time plan creation
   - Progress tracking and adaptation
   - Personalized learning paths

4. **Interactive Course Creator** (`new_agent/interactive_course_creator.py`)
   - Dynamic course generation
   - User profile-based customization
   - LLM-powered content creation

### Frontend Components

1. **Agent Service** (`frontend/src/lib/agentService.ts`)
   - TypeScript service for API communication
   - Type-safe interfaces for all agent operations
   - Error handling and response processing

2. **Enhanced CreateGoalDialog** (`frontend/src/components/CreateGoalDialog.tsx`)
   - Extended form with learning preferences
   - Real-time data loading from agent service
   - Integration with course creation API

3. **CourseResultDialog** (`frontend/src/components/CourseResultDialog.tsx`)
   - Displays generated course curriculum
   - Interactive lesson browsing
   - Learning path visualization

## API Endpoints

### Learning Plan Management
- `POST /api/agents/create-learning-plan` - Create personalized learning plan
- `GET /api/agents/learning-plan-status/{user_id}` - Get plan status

### Course Creation
- `POST /api/agents/create-course` - Create dynamic course
- `GET /api/agents/available-subjects` - Get available subjects
- `GET /api/agents/learning-styles` - Get learning styles
- `GET /api/agents/difficulty-levels` - Get difficulty levels

### Learning Sessions
- `POST /api/agents/start-learning-session` - Start learning session
- `POST /api/agents/process-interaction` - Process user interaction
- `POST /api/agents/end-learning-session/{session_id}` - End session

### Progress Tracking
- `POST /api/agents/track-progress` - Track user progress
- `GET /api/agents/system-status` - Get system status

## Data Flow

1. **User Creates Goal**
   ```
   Frontend Form → Agent Service → Backend API → Tutoring System → LLM Service
   ```

2. **Course Generation**
   ```
   User Preferences → Dynamic Planner → Curriculum Generator → AI Content Creation
   ```

3. **Learning Session**
   ```
   User Interaction → Session Manager → Adaptive Content → Progress Tracking
   ```

## Key Features

### AI-Powered Course Generation
- Dynamic curriculum creation based on user preferences
- LLM-generated lesson content
- Adaptive difficulty progression
- Personalized learning paths

### Multi-Agent System
- **Knowledge Agent**: Concept explanations and content adaptation
- **Practice Agent**: Exercise generation and assessment
- **Motivation Agent**: Progress tracking and encouragement
- **Planner Agent**: Learning path optimization

### Adaptive Learning
- Real-time difficulty adjustment
- Performance-based recommendations
- Learning curve analysis
- Gap identification and filling

## Usage Examples

### Creating a Learning Goal

```typescript
const courseRequest: CreateCourseRequest = {
  user_id: "user_123",
  subject: "Python Programming",
  topic: "Web Development",
  weeks: 8,
  focus: "practical",
  assessments: true,
  user_profile: {
    name: "John Doe",
    email: "john@example.com",
    learning_style: "visual",
    preferred_difficulty: "intermediate",
    available_time: 120,
    learning_goals: ["Master Python", "Build web apps"],
    interests: ["Programming", "Web Development"]
  }
};

const course = await agentService.createCourse(courseRequest);
```

### Tracking Progress

```typescript
const progressRequest: ProgressTrackingRequest = {
  user_id: "user_123",
  activity: "lesson_completed",
  data: {
    lesson_id: "lesson_001",
    time_spent: 45,
    score: 85
  }
};

const progress = await agentService.trackProgress(progressRequest);
```

## Configuration

### Environment Variables
```bash
# Google AI Configuration
GOOGLE_API_KEY=your_google_api_key_here

# Server Configuration
HOST=127.0.0.1
PORT=8000
DEBUG=True

# LangGraph Configuration
MAX_ITERATIONS=10
```

### Dependencies
- FastAPI for backend API
- React + TypeScript for frontend
- Google Gemini for LLM services
- LangGraph for workflow management

## Testing

Run the integration test:
```bash
python test_agent_integration.py
```

This will test:
- System initialization
- Learning plan creation
- Course generation
- System status retrieval

## Future Enhancements

1. **Real-time Collaboration**
   - Multi-user learning sessions
   - Peer-to-peer learning features
   - Collaborative projects

2. **Advanced Analytics**
   - Learning pattern analysis
   - Performance prediction
   - Personalized recommendations

3. **Integration Features**
   - External learning platforms
   - Assessment tools
   - Certification systems

## Troubleshooting

### Common Issues

1. **API Connection Errors**
   - Check backend server is running
   - Verify CORS configuration
   - Check API endpoint URLs

2. **LLM Service Errors**
   - Verify Google API key
   - Check API quota limits
   - Monitor error logs

3. **Frontend Integration Issues**
   - Check TypeScript compilation
   - Verify component imports
   - Check browser console for errors

### Debug Mode

Enable debug mode by setting `DEBUG=True` in environment variables. This will provide detailed logging for troubleshooting.

## Support

For issues or questions regarding the agent integration:
1. Check the logs for error messages
2. Verify all dependencies are installed
3. Test individual components separately
4. Review the API documentation

## License

This integration is part of the StudySpark project and follows the same licensing terms.
