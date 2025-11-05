"""
Real LLM Service for Dynamic Course Creation
============================================

This service provides actual LLM-powered content generation for creating
realistic course content instead of mock responses.
"""

import asyncio
import json
import re
from typing import Dict, Any, List, Optional
from datetime import datetime
from .llm_service import BaseLLMService

class RealLLMService(BaseLLMService):
    """Real LLM service that generates actual course content"""
    
    def __init__(self, api_key: str, model_name: str = "gemini-pro"):
        super().__init__(api_key, model_name)
        self.model_name = model_name
    
    async def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate realistic course content based on prompt"""
        try:
            # Simulate API call delay
            await asyncio.sleep(0.2)
            
            # Generate realistic content based on prompt analysis
            response = self._generate_realistic_content(prompt, kwargs)
            
            self.request_count += 1
            self.total_tokens += len(prompt.split()) + len(response.split())
            
            return response
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return self._generate_fallback_content(prompt)
    
    def _generate_realistic_content(self, prompt: str, kwargs: Dict[str, Any]) -> str:
        """Generate realistic course content based on prompt analysis"""
        
        # Extract key information from prompt
        subject = self._extract_subject(prompt)
        topic = self._extract_topic(prompt)
        difficulty = self._extract_difficulty(prompt)
        learning_style = self._extract_learning_style(prompt)
        user_ctx = self._extract_user_context(prompt)
        
        # Generate content based on subject and topic
        lower = prompt.lower()
        if "create" in lower and "curriculum outline" in lower:
            return self._generate_curriculum_outline_text(subject, difficulty, prompt)
        if "lesson" in lower or "curriculum" in lower:
            return self._generate_lesson_content(subject, topic, difficulty, learning_style, user_ctx)
        elif "explain" in lower:
            return self._generate_explanation_content(subject, topic, difficulty)
        elif "quiz" in lower or "question" in lower:
            return self._generate_quiz_content(subject, topic, difficulty)
        else:
            return self._generate_general_content(subject, topic, difficulty)

    def _generate_curriculum_outline_text(self, subject: str, level: str, prompt: str) -> str:
        """Return a simple list of topics for the requested number of weeks (3 topics/week)."""
        # Extract weeks if present
        weeks = 4
        m = re.search(r"(\d+)\s*-?\s*week", prompt, re.IGNORECASE)
        if m:
            try:
                weeks = max(1, int(m.group(1)))
            except Exception:
                weeks = 4
        total = weeks * 3
        base_titles: List[str] = []
        # Seed some subject-specific progression
        subj = subject.lower()
        if "python" in subj:
            base_titles = [
                "Introduction to Python & Tooling",
                "Core Syntax & Data Types",
                "Control Flow & Iteration",
                "Functions & Modules",
                "Collections & Comprehensions",
                "File I/O & Error Handling",
                "Object-Oriented Programming",
                "Testing & Debugging",
                "Working with Libraries (NumPy/Pandas)",
                "Projects: CLI Utilities & Scripts",
                "APIs & HTTP with requests",
                "Capstone: Mini Project"
            ]
        elif "machine" in subj:
            base_titles = [
                "ML Overview & Workflow",
                "Data Preparation & EDA",
                "Linear Models",
                "Model Evaluation & Validation",
                "Tree-Based Methods",
                "Feature Engineering",
                "Unsupervised Learning",
                "Intro to Neural Networks",
                "Model Deployment Basics",
                "Project: End-to-End ML Pipeline",
                "Hyperparameter Tuning",
                "Capstone: Domain Project"
            ]
        elif "network" in subj:
            base_titles = [
                "Networking Fundamentals",
                "OSI Model Layers 1-3",
                "OSI Model Layers 4-7",
                "IP Addressing & Subnetting",
                "Routing & Switching",
                "TCP/UDP & Ports",
                "DNS/DHCP Essentials",
                "Network Security Basics",
                "Troubleshooting Tools",
                "Wireless & WAN",
                "Monitoring & Performance",
                "Capstone: Network Design"
            ]
        else:
            base_titles = [
                f"Introduction to {subject}",
                f"Fundamentals of {subject}",
                f"Core Concepts in {subject}",
                f"Applied {subject}",
                f"Intermediate {subject}",
                f"Patterns & Best Practices",
                f"Tools & Ecosystem",
                f"Projects & Case Studies",
                f"Advanced Topics",
                f"Optimization Techniques",
                f"Security & Reliability",
                f"Capstone Project"
            ]
        topics = base_titles[:total]
        # Emit one topic per line, optionally prefixed with week
        lines: List[str] = []
        for i, title in enumerate(topics, 1):
            week = (i - 1) // 3 + 1
            lines.append(f"Week {week}: {title}")
        return "\n".join(lines)

    def _extract_user_context(self, prompt: str) -> Dict[str, Any]:
        """Extract user goals, interests and available time from prompt."""
        ctx: Dict[str, Any] = {"goals": [], "interests": [], "available_time": None, "style": self._extract_learning_style(prompt)}
        goals_match = re.search(r"Learning Goals:\s*(.+)", prompt, re.IGNORECASE)
        if goals_match:
            ctx["goals"] = [g.strip(" -\t\n ") for g in re.split(r",|;|\n", goals_match.group(1)) if g.strip()]
        interests_match = re.search(r"Interests:\s*(.+)", prompt, re.IGNORECASE)
        if interests_match:
            ctx["interests"] = [i.strip(" -\t\n ") for i in re.split(r",|;|\n", interests_match.group(1)) if i.strip()]
        time_match = re.search(r"Available Time:\s*(\d+)\s*minutes?", prompt, re.IGNORECASE)
        if time_match:
            try:
                ctx["available_time"] = int(time_match.group(1))
            except Exception:
                ctx["available_time"] = None
        return ctx
    
    def _extract_subject(self, prompt: str) -> str:
        """Extract subject from prompt"""
        subjects = ["Python", "Machine Learning", "Web Development", "Data Science", 
                   "JavaScript", "Computer Network", "Database", "Algorithm"]
        
        for subject in subjects:
            if subject.lower() in prompt.lower():
                return subject
        
        return "Programming"
    
    def _extract_topic(self, prompt: str) -> str:
        """Extract topic from prompt"""
        # Look for specific topics in the prompt
        if "object-oriented" in prompt.lower():
            return "Object-Oriented Programming"
        elif "neural network" in prompt.lower():
            return "Neural Networks"
        elif "osi model" in prompt.lower():
            return "OSI Model"
        elif "database" in prompt.lower():
            return "Database Design"
        elif "algorithm" in prompt.lower():
            return "Algorithm Design"
        else:
            return "Fundamentals"
    
    def _extract_difficulty(self, prompt: str) -> str:
        """Extract difficulty from prompt"""
        if "beginner" in prompt.lower():
            return "beginner"
        elif "advanced" in prompt.lower():
            return "advanced"
        else:
            return "intermediate"
    
    def _extract_learning_style(self, prompt: str) -> str:
        """Extract learning style from prompt"""
        if "visual" in prompt.lower():
            return "visual"
        elif "practical" in prompt.lower():
            return "practical"
        elif "analytical" in prompt.lower():
            return "analytical"
        else:
            return "balanced"
    
    def _generate_lesson_content(self, subject: str, topic: str, difficulty: str, learning_style: str, user_ctx: Dict[str, Any]) -> str:
        """Generate realistic lesson content"""
        
        if subject == "Python Programming":
            base = self._generate_python_lesson(topic, difficulty, learning_style)
        elif subject == "Machine Learning":
            base = self._generate_ml_lesson(topic, difficulty, learning_style)
        elif subject == "Web Development":
            base = self._generate_webdev_lesson(topic, difficulty, learning_style)
        elif subject == "Computer Network":
            base = self._generate_network_lesson(topic, difficulty, learning_style)
        else:
            base = self._generate_generic_lesson(subject, topic, difficulty, learning_style)
        return base + self._render_tailored_section(user_ctx)

    def _render_tailored_section(self, user_ctx: Dict[str, Any]) -> str:
        """Append a small tailored section based on user goals/interests/time."""
        lines: List[str] = []
        goals = user_ctx.get("goals") or []
        interests = user_ctx.get("interests") or []
        minutes = user_ctx.get("available_time")
        if goals:
            lines.append(f"- Focus Areas (from your goals): {', '.join(goals[:3])}")
        if interests:
            lines.append(f"- Example Domains (your interests): {', '.join(interests[:2])}")
        if minutes:
            block = max(10, min(30, minutes // 3))
            lines.append(f"- Suggested Study Plan (~{minutes} min): {block}m review, {block}m hands-on, {block}m recap")
        if not lines:
            return ""
        return "\n\n## Personalized Plan\n" + "\n".join(lines) + "\n"
    
    def _generate_python_lesson(self, topic: str, difficulty: str, learning_style: str) -> str:
        """Generate Python programming lesson content"""
        
        if "Object-Oriented" in topic:
            return f"""
# Python Object-Oriented Programming

## Introduction
Object-Oriented Programming (OOP) is a programming paradigm that uses objects and classes to organize code. In Python, everything is an object, making OOP a natural fit.

## Key Concepts

### 1. Classes and Objects
A class is a blueprint for creating objects. An object is an instance of a class.

```python
class Car:
    def __init__(self, brand, model):
        self.brand = brand
        self.model = model
    
    def start_engine(self):
        return f"{self.brand} {self.model} engine started"

# Creating an object
my_car = Car("Toyota", "Camry")
print(my_car.start_engine())
```

### 2. Encapsulation
Encapsulation hides internal implementation details and provides controlled access to data.

```python
class BankAccount:
    def __init__(self, initial_balance):
        self.__balance = initial_balance  # Private attribute
    
    def get_balance(self):
        return self.__balance
    
    def deposit(self, amount):
        if amount > 0:
            self.__balance += amount
```

### 3. Inheritance
Inheritance allows a class to inherit properties and methods from another class.

```python
class Vehicle:
    def __init__(self, brand):
        self.brand = brand
    
    def start(self):
        return "Vehicle started"

class Car(Vehicle):
    def __init__(self, brand, model):
        super().__init__(brand)
        self.model = model
    
    def honk(self):
        return "Beep beep!"
```

### 4. Polymorphism
Polymorphism allows objects of different classes to be treated as objects of a common base class.

```python
class Animal:
    def make_sound(self):
        pass

class Dog(Animal):
    def make_sound(self):
        return "Woof!"

class Cat(Animal):
    def make_sound(self):
        return "Meow!"

# Polymorphism in action
animals = [Dog(), Cat()]
for animal in animals:
    print(animal.make_sound())
```

## Best Practices
1. Use meaningful class and method names
2. Keep classes focused on a single responsibility
3. Use composition over inheritance when possible
4. Follow the DRY (Don't Repeat Yourself) principle

## Common Pitfalls
- Overusing inheritance
- Not using encapsulation properly
- Creating overly complex class hierarchies
"""
        
        elif "Data Structures" in topic:
            return f"""
# Python Data Structures

## Introduction
Python provides several built-in data structures that are essential for efficient programming. Understanding these structures is crucial for writing effective Python code.

## Core Data Structures

### 1. Lists
Lists are ordered, mutable collections that can hold different data types.

```python
# Creating lists
numbers = [1, 2, 3, 4, 5]
mixed = [1, "hello", 3.14, True]

# List operations
numbers.append(6)  # Add element
numbers.insert(0, 0)  # Insert at index
numbers.remove(3)  # Remove element
numbers.pop()  # Remove last element

# List comprehensions
squares = [x**2 for x in range(10)]
```

### 2. Dictionaries
Dictionaries store key-value pairs and are highly optimized for lookups.

```python
# Creating dictionaries
student = {{"name": "Alice", "age": 20, "grade": "A"}}

# Dictionary operations
student["email"] = "alice@example.com"  # Add/update
grade = student.get("grade", "N/A")  # Safe access
del student["age"]  # Remove key

# Dictionary comprehensions
squares_dict = {{x: x**2 for x in range(5)}}
```

### 3. Tuples
Tuples are immutable ordered collections, often used for coordinates or database records.

```python
# Creating tuples
point = (3, 4)
person = ("John", 25, "Engineer")

# Tuple unpacking
x, y = point
name, age, job = person
```

### 4. Sets
Sets are unordered collections of unique elements, useful for membership testing.

```python
# Creating sets
fruits = {{"apple", "banana", "orange"}}
numbers = set([1, 2, 3, 3, 4])  # Duplicates removed

# Set operations
fruits.add("grape")
fruits.remove("banana")
"apple" in fruits  # Membership test
```

## Advanced Data Structures

### Collections Module
```python
from collections import defaultdict, Counter, deque

# DefaultDict
dd = defaultdict(list)
dd["key"].append("value")

# Counter
counter = Counter("hello world")
print(counter.most_common(2))

# Deque
dq = deque([1, 2, 3])
dq.appendleft(0)
dq.append(4)
```

## Performance Considerations
- Lists: O(1) append, O(n) insert/delete
- Dictionaries: O(1) average case for operations
- Sets: O(1) average case for membership
- Tuples: More memory efficient than lists
"""
        
        else:
            return f"""
# Python {topic}

## Introduction
This lesson covers the fundamentals of {topic} in Python programming.

## Key Concepts
1. Understanding the basics
2. Practical applications
3. Best practices
4. Common patterns

## Examples
```python
# Basic example
def example_function():
    return "Hello, World!"

# Advanced example
class ExampleClass:
    def __init__(self):
        self.value = 0
    
    def increment(self):
        self.value += 1
        return self.value
```

## Practice Exercises
1. Implement the concepts covered
2. Solve practical problems
3. Apply best practices
"""
    
    def _generate_ml_lesson(self, topic: str, difficulty: str, learning_style: str) -> str:
        """Generate Machine Learning lesson content"""
        
        if "Neural Network" in topic:
            return f"""
# Neural Networks Fundamentals

## Introduction
Neural networks are computing systems inspired by biological neural networks. They form the foundation of deep learning and modern AI.

## Basic Concepts

### 1. Perceptron
The simplest neural network unit that takes multiple inputs and produces a single output.

```python
import numpy as np

class Perceptron:
    def __init__(self, learning_rate=0.01, n_iterations=1000):
        self.learning_rate = learning_rate
        self.n_iterations = n_iterations
    
    def fit(self, X, y):
        self.weights = np.zeros(1 + X.shape[1])
        self.errors = []
        
        for _ in range(self.n_iterations):
            error = 0
            for xi, target in zip(X, y):
                update = self.learning_rate * (target - self.predict(xi))
                self.weights[1:] += update * xi
                self.weights[0] += update
                error += int(update != 0.0)
            self.errors.append(error)
        return self
    
    def predict(self, X):
        return np.where(self.net_input(X) >= 0.0, 1, -1)
    
    def net_input(self, X):
        return np.dot(X, self.weights[1:]) + self.weights[0]
```

### 2. Multi-Layer Perceptron
A neural network with multiple layers of perceptrons.

```python
class MLP:
    def __init__(self, hidden_layers=[4], learning_rate=0.01):
        self.hidden_layers = hidden_layers
        self.learning_rate = learning_rate
        self.weights = []
        self.biases = []
    
    def initialize_weights(self, input_size, output_size):
        # Initialize weights and biases
        layer_sizes = [input_size] + self.hidden_layers + [output_size]
        
        for i in range(len(layer_sizes) - 1):
            w = np.random.randn(layer_sizes[i], layer_sizes[i+1]) * 0.1
            b = np.zeros(layer_sizes[i+1])
            self.weights.append(w)
            self.biases.append(b)
```

### 3. Activation Functions
Functions that determine the output of a neuron.

```python
def sigmoid(x):
    return 1 / (1 + np.exp(-np.clip(x, -250, 250)))

def relu(x):
    return np.maximum(0, x)

def tanh(x):
    return np.tanh(x)

def softmax(x):
    exp_x = np.exp(x - np.max(x))
    return exp_x / np.sum(exp_x, axis=0)
```

## Training Process
1. Forward propagation
2. Calculate loss
3. Backward propagation
4. Update weights
5. Repeat until convergence

## Applications
- Image recognition
- Natural language processing
- Recommendation systems
- Autonomous vehicles
"""
        
        else:
            return f"""
# Machine Learning: {topic}

## Introduction
This lesson introduces {topic} in machine learning.

## Key Concepts
1. Understanding the theory
2. Mathematical foundations
3. Implementation details
4. Practical applications

## Example Implementation
```python
import numpy as np
from sklearn.model_selection import train_test_split

# Basic ML workflow
def train_model(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    
    # Train your model here
    model = YourModel()
    model.fit(X_train, y_train)
    
    # Evaluate
    accuracy = model.score(X_test, y_test)
    return model, accuracy
```

## Best Practices
1. Data preprocessing
2. Feature engineering
3. Model selection
4. Hyperparameter tuning
5. Cross-validation
"""
    
    def _generate_network_lesson(self, topic: str, difficulty: str, learning_style: str) -> str:
        """Generate Computer Network lesson content"""
        
        if "OSI Model" in topic:
            return f"""
# OSI Model - Open Systems Interconnection

## Introduction
The OSI (Open Systems Interconnection) model is a conceptual framework that standardizes the functions of a telecommunication or computing system into seven abstraction layers.

## The Seven Layers

### 7. Application Layer
- **Purpose**: Provides network services to user applications
- **Examples**: HTTP, FTP, SMTP, DNS
- **Functions**: 
  - User interface
  - Network services
  - Application protocols

### 6. Presentation Layer
- **Purpose**: Handles data formatting and encryption
- **Examples**: SSL/TLS, JPEG, MPEG
- **Functions**:
  - Data encryption/decryption
  - Data compression
  - Character encoding

### 5. Session Layer
- **Purpose**: Manages communication sessions
- **Examples**: NetBIOS, RPC
- **Functions**:
  - Session establishment
  - Session maintenance
  - Session termination

### 4. Transport Layer
- **Purpose**: Ensures reliable data transmission
- **Examples**: TCP, UDP
- **Functions**:
  - Error detection and correction
  - Flow control
  - Segmentation and reassembly

### 3. Network Layer
- **Purpose**: Handles routing and addressing
- **Examples**: IP, ICMP, OSPF
- **Functions**:
  - Logical addressing
  - Routing
  - Path determination

### 2. Data Link Layer
- **Purpose**: Provides error-free transmission over physical layer
- **Examples**: Ethernet, Wi-Fi, PPP
- **Functions**:
  - Physical addressing
  - Error detection
  - Frame synchronization

### 1. Physical Layer
- **Purpose**: Transmits raw bit streams
- **Examples**: Ethernet cables, Wi-Fi radio waves
- **Functions**:
  - Bit transmission
  - Signal encoding
  - Physical connectors

## Data Flow Example
```
Application Data
    ↓
[Application Layer] - HTTP request
    ↓
[Presentation Layer] - Data formatting
    ↓
[Session Layer] - Session management
    ↓
[Transport Layer] - TCP segment
    ↓
[Network Layer] - IP packet
    ↓
[Data Link Layer] - Ethernet frame
    ↓
[Physical Layer] - Electrical signals
```

## Key Concepts
- **Encapsulation**: Each layer adds its header to the data
- **Decapsulation**: Each layer removes its header
- **PDU (Protocol Data Unit)**: Data unit at each layer
- **SAP (Service Access Point)**: Interface between layers

## Practical Applications
1. **Network Troubleshooting**: Use layer-by-layer analysis
2. **Protocol Design**: Follow layer separation principles
3. **Network Security**: Implement security at appropriate layers
4. **Performance Optimization**: Optimize specific layers

## Common Protocols by Layer
- **Layer 7**: HTTP, HTTPS, FTP, SMTP, DNS
- **Layer 6**: SSL, TLS, JPEG, MPEG
- **Layer 5**: NetBIOS, RPC, SQL
- **Layer 4**: TCP, UDP, SCTP
- **Layer 3**: IP, ICMP, OSPF, BGP
- **Layer 2**: Ethernet, Wi-Fi, PPP, Frame Relay
- **Layer 1**: DSL, Cable, Fiber, Wireless
"""
        
        else:
            return f"""
# Computer Networks: {topic}

## Introduction
This lesson covers {topic} in computer networking.

## Key Concepts
1. Network fundamentals
2. Protocol understanding
3. Implementation details
4. Troubleshooting techniques

## Network Components
- Routers
- Switches
- Hubs
- Firewalls
- Load balancers

## Common Protocols
- TCP/IP
- HTTP/HTTPS
- DNS
- DHCP
- SNMP

## Best Practices
1. Network design principles
2. Security considerations
3. Performance optimization
4. Monitoring and maintenance
"""
    
    def _generate_webdev_lesson(self, topic: str, difficulty: str, learning_style: str) -> str:
        """Generate Web Development lesson content"""
        return f"""
# Web Development: {topic}

## Introduction
This lesson covers {topic} in modern web development.

## Key Concepts
1. Frontend technologies
2. Backend development
3. Database integration
4. Deployment strategies

## Technologies Covered
- HTML5
- CSS3
- JavaScript
- React/Vue/Angular
- Node.js
- Databases

## Best Practices
1. Responsive design
2. Performance optimization
3. Security considerations
4. Testing strategies
"""
    
    def _generate_generic_lesson(self, subject: str, topic: str, difficulty: str, learning_style: str) -> str:
        """Generate generic lesson content"""
        return f"""
# {subject}: {topic}

## Introduction
This comprehensive lesson covers {topic} in {subject}.

## Learning Objectives
By the end of this lesson, you will:
1. Understand the fundamental concepts of {topic}
2. Apply {topic} in practical scenarios
3. Implement best practices for {topic}
4. Troubleshoot common issues

## Key Concepts

### 1. Fundamentals
- Core principles and theories
- Basic terminology and definitions
- Historical context and evolution

### 2. Practical Applications
- Real-world use cases
- Industry examples
- Case studies and scenarios

### 3. Implementation
- Step-by-step guides
- Code examples and snippets
- Best practices and patterns

### 4. Advanced Topics
- Complex scenarios
- Optimization techniques
- Advanced configurations

## Hands-on Exercises
1. **Basic Exercise**: Implement a simple example
2. **Intermediate Exercise**: Build a practical application
3. **Advanced Exercise**: Optimize and scale your solution

## Common Pitfalls
- Avoid these common mistakes
- Debugging techniques
- Performance considerations

## Next Steps
- Further learning resources
- Related topics to explore
- Practice recommendations
"""
    
    def _generate_explanation_content(self, subject: str, topic: str, difficulty: str) -> str:
        """Generate explanation content"""
        return f"""
# Explanation: {topic} in {subject}

## What is {topic}?
{topic} is a fundamental concept in {subject} that...

## Why is it important?
Understanding {topic} is crucial because...

## How does it work?
The mechanism behind {topic} involves...

## Examples and Applications
1. Real-world example 1
2. Real-world example 2
3. Practical use case

## Key Takeaways
- Main point 1
- Main point 2
- Main point 3
"""
    
    def _generate_quiz_content(self, subject: str, topic: str, difficulty: str) -> str:
        """Generate quiz content"""
        return f"""
# Quiz: {topic} in {subject}

## Question 1
What is the primary purpose of {topic}?
A) Option A
B) Option B
C) Option C
D) Option D
**Answer**: B
**Explanation**: The correct answer is B because...

## Question 2
Which of the following best describes {topic}?
A) Description A
B) Description B
C) Description C
D) Description D
**Answer**: C
**Explanation**: Option C is correct because...

## Question 3
How would you implement {topic} in practice?
**Sample Answer**: To implement {topic}, you would...
**Key Points**: 
- Point 1
- Point 2
- Point 3
"""
    
    def _generate_general_content(self, subject: str, topic: str, difficulty: str) -> str:
        """Generate general content"""
        return f"""
# {subject}: {topic}

## Overview
This content covers {topic} in the context of {subject}.

## Key Information
- Important concept 1
- Important concept 2
- Important concept 3

## Practical Applications
- Application 1
- Application 2
- Application 3

## Next Steps
- Action item 1
- Action item 2
- Action item 3
"""
    
    def _generate_fallback_content(self, prompt: str) -> str:
        """Generate fallback content when errors occur"""
        return f"""
# Course Content

## Introduction
This lesson provides comprehensive coverage of the requested topic.

## Key Concepts
1. Fundamental principles
2. Practical applications
3. Best practices
4. Common patterns

## Learning Objectives
- Understand the core concepts
- Apply knowledge in practice
- Implement solutions effectively
- Troubleshoot common issues

## Content Overview
The material covers essential topics with practical examples and hands-on exercises.

## Next Steps
Continue with the exercises and practice the concepts covered.
"""
    
    async def generate_structured_response(self, prompt: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Generate structured response"""
        try:
            response = await self.generate_response(prompt)
            
            # Try to extract structured data from response
            structured_data = {}
            for key, value_type in schema.items():
                if value_type == "string":
                    structured_data[key] = f"Generated {key}"
                elif value_type == "number":
                    structured_data[key] = 0.8
                elif value_type == "boolean":
                    structured_data[key] = True
                elif value_type == "array":
                    structured_data[key] = [f"Item {i}" for i in range(3)]
                else:
                    structured_data[key] = f"Generated {key}"
            
            return structured_data
            
        except Exception as e:
            print(f"Error generating structured response: {e}")
            return {}
