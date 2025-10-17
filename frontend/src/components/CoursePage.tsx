import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";
import agentService from "@/lib/agentService";
import dynamicCourseService from "@/lib/dynamicCourseService";
import { useAuth } from "@/store/AuthContext";

interface TopicItem {
  id: string;
  title: string;
  difficulty: string;
  duration: number;
  subtopics?: { title: string; deadline_minutes: number }[];
  questions?: any[];
  description?: string;
  learningObjectives?: string[];
  examples?: {
    title: string;
    description: string;
    code?: string;
    image?: string;
  }[];
  concepts?: {
    title: string;
    explanation: string;
    image?: string;
  }[];
  prerequisites?: string[];
}

const CoursePage = () => {
  const { courseId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [title, setTitle] = useState<string>("Course");
  const [topics, setTopics] = useState<TopicItem[]>([]);
  const [isDynamicCourse, setIsDynamicCourse] = useState(false);
  const [showSubtopics, setShowSubtopics] = useState(false);
  const [selectedTopic, setSelectedTopic] = useState<TopicItem | null>(null);
  const [activeLesson, setActiveLesson] = useState<TopicItem | null>(null);
  const [lessonProgress, setLessonProgress] = useState(0);

  // Dummy topics data for different subjects
  const getDummyTopics = (courseId: string): TopicItem[] => {
    const dummyTopicsMap: { [key: string]: TopicItem[] } = {
      "1": [ // Advanced Mathematics
        {
          id: "math-1",
          title: "Calculus Fundamentals",
          difficulty: "Intermediate",
          duration: 45,
          description: "Master the core concepts of calculus including limits, derivatives, and their applications in real-world problems.",
          learningObjectives: [
            "Understand the concept of limits and continuity",
            "Calculate derivatives using various rules",
            "Apply derivatives to solve optimization problems",
            "Interpret the meaning of derivatives in context"
          ],
          prerequisites: ["Basic Algebra", "Trigonometry", "Functions"],
          subtopics: [
            { title: "Limits and Continuity", deadline_minutes: 20 },
            { title: "Derivatives", deadline_minutes: 25 }
          ],
          concepts: [
            {
              title: "Limits",
              explanation: "A limit describes the behavior of a function as its input approaches a particular value. It's the foundation of calculus.",
              image: "https://images.unsplash.com/photo-1635070041078-e363dbe005cb?w=400&h=300&fit=crop"
            },
            {
              title: "Derivatives",
              explanation: "A derivative represents the rate of change of a function at any point. It tells us how fast something is changing.",
              image: "https://images.unsplash.com/photo-1509228468518-180dd4864904?w=400&h=300&fit=crop"
            }
          ],
          examples: [
            {
              title: "Finding the Limit of a Function",
              description: "Let's find the limit of f(x) = x² as x approaches 2",
              code: "lim(x→2) x² = 2² = 4",
              image: "https://images.unsplash.com/photo-1596495578065-6e0763fa1178?w=400&h=300&fit=crop"
            },
            {
              title: "Derivative of a Polynomial",
              description: "Find the derivative of f(x) = 3x² + 2x + 1",
              code: "f'(x) = d/dx(3x²) + d/dx(2x) + d/dx(1)\n= 6x + 2 + 0\n= 6x + 2",
              image: "https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=400&h=300&fit=crop"
            }
          ],
          questions: [
            { 
              id: "math-calc-1",
              question: "What is the limit of f(x) = x² as x approaches 2?", 
              type: "multiple_choice",
              options: [
                { text: "2", correct: false },
                { text: "4", correct: true },
                { text: "6", correct: false },
                { text: "8", correct: false }
              ]
            },
            { 
              id: "math-calc-2",
              question: "Find the derivative of f(x) = 3x² + 2x + 1", 
              type: "multiple_choice",
              options: [
                { text: "6x + 2", correct: true },
                { text: "3x + 2", correct: false },
                { text: "6x + 1", correct: false },
                { text: "3x² + 2", correct: false }
              ]
            },
            { 
              id: "math-calc-3",
              question: "What is the integral of 2x with respect to x?", 
              type: "multiple_choice",
              options: [
                { text: "x² + C", correct: true },
                { text: "2x² + C", correct: false },
                { text: "x + C", correct: false },
                { text: "2x + C", correct: false }
              ]
            },
            { 
              id: "math-calc-4",
              question: "Explain the concept of continuity in calculus", 
              type: "short_answer"
            }
          ]
        },
        {
          id: "math-2",
          title: "Linear Algebra",
          difficulty: "Advanced",
          duration: 60,
          description: "Explore vector spaces, matrix operations, and linear transformations that form the backbone of modern mathematics and computer science.",
          learningObjectives: [
            "Understand vector spaces and their properties",
            "Perform matrix operations and transformations",
            "Solve systems of linear equations",
            "Apply linear algebra concepts to real-world problems"
          ],
          prerequisites: ["Calculus Fundamentals", "Basic Matrix Operations"],
          subtopics: [
            { title: "Vector Spaces", deadline_minutes: 30 },
            { title: "Matrix Operations", deadline_minutes: 30 }
          ],
          concepts: [
            {
              title: "Vector Spaces",
              explanation: "A vector space is a collection of vectors that can be added together and multiplied by scalars, following specific rules.",
              image: "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=400&h=300&fit=crop"
            },
            {
              title: "Matrix Operations",
              explanation: "Matrices are rectangular arrays of numbers that can be added, multiplied, and transformed to solve complex problems.",
              image: "https://images.unsplash.com/photo-1611224923853-80b023f02d71?w=400&h=300&fit=crop"
            }
          ],
          examples: [
            {
              title: "Matrix Multiplication",
              description: "Multiply two 2x2 matrices A and B",
              code: "A = [[1, 2], [3, 4]]\nB = [[5, 6], [7, 8]]\nAB = [[1×5+2×7, 1×6+2×8], [3×5+4×7, 3×6+4×8]]\n= [[19, 22], [43, 50]]",
              image: "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=400&h=300&fit=crop"
            },
            {
              title: "Dot Product of Vectors",
              description: "Calculate the dot product of vectors [1,2,3] and [4,5,6]",
              code: "a · b = 1×4 + 2×5 + 3×6\n= 4 + 10 + 18\n= 32",
              image: "https://images.unsplash.com/photo-1611224923853-80b023f02d71?w=400&h=300&fit=crop"
            }
          ],
          questions: [
            { 
              id: "math-linalg-1",
              question: "What is the determinant of a 2x2 matrix [[a,b],[c,d]]?", 
              type: "multiple_choice",
              options: [
                { text: "ad-bc", correct: true },
                { text: "ad+bc", correct: false },
                { text: "ac-bd", correct: false },
                { text: "ac+bd", correct: false }
              ]
            },
            { 
              id: "math-linalg-2",
              question: "What is the rank of the matrix [[1,2],[2,4]]?", 
              type: "multiple_choice",
              options: [
                { text: "0", correct: false },
                { text: "1", correct: true },
                { text: "2", correct: false },
                { text: "4", correct: false }
              ]
            },
            { 
              id: "math-linalg-3",
              question: "Explain what a vector space is and give an example", 
              type: "short_answer"
            },
            { 
              id: "math-linalg-4",
              question: "What is the dot product of vectors [1,2,3] and [4,5,6]?", 
              type: "multiple_choice",
              options: [
                { text: "32", correct: true },
                { text: "15", correct: false },
                { text: "21", correct: false },
                { text: "45", correct: false }
              ]
            }
          ]
        },
        {
          id: "math-3",
          title: "Differential Equations",
          difficulty: "Advanced",
          duration: 50,
          description: "Learn to solve differential equations and understand their applications in modeling real-world phenomena.",
          learningObjectives: [
            "Solve first-order differential equations",
            "Understand second-order differential equations",
            "Apply differential equations to real-world problems",
            "Use various solution techniques"
          ],
          prerequisites: ["Calculus Fundamentals", "Linear Algebra"],
          subtopics: [
            { title: "First Order DE", deadline_minutes: 25 },
            { title: "Second Order DE", deadline_minutes: 25 }
          ],
          concepts: [
            {
              title: "First Order Differential Equations",
              explanation: "Equations involving the first derivative of a function. They describe many natural phenomena.",
              image: "https://images.unsplash.com/photo-1509228468518-180dd4864904?w=400&h=300&fit=crop"
            },
            {
              title: "Second Order Differential Equations",
              explanation: "Equations involving the second derivative, commonly found in physics and engineering.",
              image: "https://images.unsplash.com/photo-1635070041078-e363dbe005cb?w=400&h=300&fit=crop"
            }
          ],
          examples: [
            {
              title: "Solving dy/dx = 2x",
              description: "Find the general solution to this first-order differential equation",
              code: "dy/dx = 2x\ndy = 2x dx\n∫dy = ∫2x dx\ny = x² + C",
              image: "https://images.unsplash.com/photo-1509228468518-180dd4864904?w=400&h=300&fit=crop"
            }
          ],
          questions: [
            { 
              id: "math-de-1",
              question: "What is the general solution to dy/dx = 2x?", 
              type: "multiple_choice",
              options: [
                { text: "y = x² + C", correct: true },
                { text: "y = 2x + C", correct: false },
                { text: "y = x²", correct: false },
                { text: "y = 2x² + C", correct: false }
              ]
            },
            { 
              id: "math-de-2",
              question: "What type of differential equation is dy/dx + P(x)y = Q(x)?", 
              type: "multiple_choice",
              options: [
                { text: "Separable", correct: false },
                { text: "Linear first-order", correct: true },
                { text: "Homogeneous", correct: false },
                { text: "Exact", correct: false }
              ]
            },
            { 
              id: "math-de-3",
              question: "Explain the difference between ordinary and partial differential equations", 
              type: "short_answer"
            }
          ]
        }
      ],
      "2": [ // Physics Fundamentals
        {
          id: "physics-1",
          title: "Mechanics",
          difficulty: "Beginner",
          duration: 40,
          description: "Study the motion of objects and the forces that cause them to move. Learn Newton's laws and their applications.",
          learningObjectives: [
            "Understand Newton's three laws of motion",
            "Calculate forces and accelerations",
            "Solve problems involving motion",
            "Apply conservation laws"
          ],
          prerequisites: ["Basic Mathematics", "Algebra"],
          subtopics: [
            { title: "Newton's Laws", deadline_minutes: 20 },
            { title: "Kinematics", deadline_minutes: 20 }
          ],
          concepts: [
            {
              title: "Newton's First Law",
              explanation: "An object at rest stays at rest, and an object in motion stays in motion, unless acted upon by an external force.",
              image: "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400&h=300&fit=crop"
            },
            {
              title: "Kinematics",
              explanation: "The study of motion without considering the forces that cause it. Describes position, velocity, and acceleration.",
              image: "https://images.unsplash.com/photo-1446776877081-d282a0f896e2?w=400&h=300&fit=crop"
            }
          ],
          examples: [
            {
              title: "Free Fall Motion",
              description: "Calculate the time for an object to fall 100 meters",
              code: "h = ½gt²\n100 = ½(9.8)t²\nt² = 20.4\nt = 4.52 seconds",
              image: "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400&h=300&fit=crop"
            }
          ],
          questions: [
            { 
              id: "physics-mech-1",
              question: "What is Newton's First Law?", 
              type: "multiple_choice",
              options: [
                { text: "F=ma", correct: false },
                { text: "An object at rest stays at rest", correct: true },
                { text: "Every action has an equal reaction", correct: false },
                { text: "Energy is conserved", correct: false }
              ]
            },
            { 
              id: "physics-mech-2",
              question: "What is the formula for kinetic energy?", 
              type: "multiple_choice",
              options: [
                { text: "KE = ½mv²", correct: true },
                { text: "KE = mv", correct: false },
                { text: "KE = mgh", correct: false },
                { text: "KE = ½mv", correct: false }
              ]
            },
            { 
              id: "physics-mech-3",
              question: "Explain the concept of momentum and give an example", 
              type: "short_answer"
            },
            { 
              id: "physics-mech-4",
              question: "What is the acceleration due to gravity on Earth?", 
              type: "multiple_choice",
              options: [
                { text: "9.8 m/s²", correct: true },
                { text: "10 m/s²", correct: false },
                { text: "9.8 m/s", correct: false },
                { text: "32 ft/s²", correct: false }
              ]
            }
          ]
        },
        {
          id: "physics-2",
          title: "Thermodynamics",
          difficulty: "Intermediate",
          duration: 55,
          description: "Study heat, temperature, and energy transfer. Understand the laws of thermodynamics and their applications.",
          learningObjectives: [
            "Understand the laws of thermodynamics",
            "Calculate heat transfer and work",
            "Apply thermodynamic principles to engines",
            "Understand entropy and disorder"
          ],
          prerequisites: ["Mechanics", "Basic Chemistry"],
          subtopics: [
            { title: "Heat Transfer", deadline_minutes: 30 },
            { title: "Entropy", deadline_minutes: 25 }
          ],
          concepts: [
            {
              title: "First Law of Thermodynamics",
              explanation: "Energy cannot be created or destroyed, only transferred or converted from one form to another.",
              image: "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&h=300&fit=crop"
            },
            {
              title: "Second Law of Thermodynamics",
              explanation: "The entropy of an isolated system always increases over time.",
              image: "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&h=300&fit=crop"
            }
          ],
          examples: [
            {
              title: "Heat Engine Efficiency",
              description: "Calculate the efficiency of a heat engine operating between two temperatures",
              code: "η = 1 - (T_cold/T_hot)\nη = 1 - (300K/500K)\nη = 0.4 = 40%",
              image: "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&h=300&fit=crop"
            }
          ],
          questions: [
            { 
              id: "physics-thermo-1",
              question: "What is the first law of thermodynamics?", 
              type: "multiple_choice",
              options: [
                { text: "Energy cannot be created or destroyed", correct: true },
                { text: "Entropy always increases", correct: false },
                { text: "Heat flows from hot to cold", correct: false },
                { text: "Temperature is constant", correct: false }
              ]
            },
            { 
              id: "physics-thermo-2",
              question: "What is the unit of entropy?", 
              type: "multiple_choice",
              options: [
                { text: "Joules per Kelvin", correct: true },
                { text: "Joules", correct: false },
                { text: "Kelvin", correct: false },
                { text: "Watts", correct: false }
              ]
            },
            { 
              id: "physics-thermo-3",
              question: "Explain the concept of heat capacity", 
              type: "short_answer"
            }
          ]
        },
        {
          id: "physics-3",
          title: "Electromagnetism",
          difficulty: "Advanced",
          duration: 65,
          description: "Explore electric and magnetic fields, their interactions, and applications in technology.",
          learningObjectives: [
            "Understand electric and magnetic fields",
            "Apply Coulomb's law and Ampere's law",
            "Understand electromagnetic induction",
            "Solve problems involving electromagnetic forces"
          ],
          prerequisites: ["Mechanics", "Calculus"],
          subtopics: [
            { title: "Electric Fields", deadline_minutes: 35 },
            { title: "Magnetic Fields", deadline_minutes: 30 }
          ],
          concepts: [
            {
              title: "Electric Fields",
              explanation: "A region around a charged particle where other charged particles experience a force.",
              image: "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&h=300&fit=crop"
            },
            {
              title: "Magnetic Fields",
              explanation: "A region around a magnet or current-carrying wire where magnetic forces are experienced.",
              image: "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&h=300&fit=crop"
            }
          ],
          examples: [
            {
              title: "Coulomb's Law",
              description: "Calculate the force between two point charges",
              code: "F = k(q₁q₂)/r²\nF = (9×10⁹)(1×10⁻⁶)(2×10⁻⁶)/(0.1)²\nF = 1.8 N",
              image: "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&h=300&fit=crop"
            }
          ],
          questions: [
            { 
              id: "physics-em-1",
              question: "What is Coulomb's law?", 
              type: "multiple_choice",
              options: [
                { text: "F = k(q₁q₂)/r²", correct: true },
                { text: "F = ma", correct: false },
                { text: "F = qvB", correct: false },
                { text: "F = kx", correct: false }
              ]
            },
            { 
              id: "physics-em-2",
              question: "What is the direction of magnetic field around a current-carrying wire?", 
              type: "multiple_choice",
              options: [
                { text: "Right-hand rule", correct: true },
                { text: "Left-hand rule", correct: false },
                { text: "Clockwise", correct: false },
                { text: "Counter-clockwise", correct: false }
              ]
            },
            { 
              id: "physics-em-3",
              question: "Explain the relationship between electric and magnetic fields", 
              type: "short_answer"
            }
          ]
        }
      ],
      "3": [ // Chemistry Review
        {
          id: "chem-1",
          title: "Organic Chemistry",
          difficulty: "Intermediate",
          duration: 50,
          description: "Study carbon-based compounds, their structure, properties, and reactions. Essential for understanding life and materials.",
          learningObjectives: [
            "Understand organic compound structures",
            "Identify functional groups",
            "Predict chemical reactions",
            "Apply IUPAC naming conventions"
          ],
          prerequisites: ["Basic Chemistry", "Chemical Bonding"],
          subtopics: [
            { title: "Alkanes and Alkenes", deadline_minutes: 25 },
            { title: "Functional Groups", deadline_minutes: 25 }
          ],
          concepts: [
            {
              title: "Carbon Bonding",
              explanation: "Carbon forms four covalent bonds, allowing for diverse molecular structures.",
              image: "https://images.unsplash.com/photo-1532187863486-abf9dbad1b69?w=400&h=300&fit=crop"
            },
            {
              title: "Functional Groups",
              explanation: "Specific groups of atoms that determine the chemical properties of organic compounds.",
              image: "https://images.unsplash.com/photo-1532187863486-abf9dbad1b69?w=400&h=300&fit=crop"
            }
          ],
          examples: [
            {
              title: "Alkane Naming",
              description: "Name the compound CH₃CH₂CH₃",
              code: "CH₃-CH₂-CH₃\n3 carbons = propane\nIUPAC name: Propane",
              image: "https://images.unsplash.com/photo-1532187863486-abf9dbad1b69?w=400&h=300&fit=crop"
            }
          ],
          questions: [
            { 
              id: "chem-org-1",
              question: "What is the general formula for alkanes?", 
              type: "multiple_choice",
              options: [
                { text: "CnH2n", correct: false },
                { text: "CnH2n+2", correct: true },
                { text: "CnH2n-2", correct: false },
                { text: "CnHn", correct: false }
              ]
            },
            { 
              id: "chem-org-2",
              question: "What functional group is present in alcohols?", 
              type: "multiple_choice",
              options: [
                { text: "-OH", correct: true },
                { text: "-COOH", correct: false },
                { text: "-CHO", correct: false },
                { text: "-NH2", correct: false }
              ]
            },
            { 
              id: "chem-org-3",
              question: "Explain the difference between alkanes, alkenes, and alkynes", 
              type: "short_answer"
            },
            { 
              id: "chem-org-4",
              question: "What is the IUPAC name for CH₃CH₂CH₃?", 
              type: "multiple_choice",
              options: [
                { text: "Propane", correct: true },
                { text: "Ethane", correct: false },
                { text: "Butane", correct: false },
                { text: "Methane", correct: false }
              ]
            }
          ]
        },
        {
          id: "chem-2",
          title: "Inorganic Chemistry",
          difficulty: "Beginner",
          duration: 45,
          description: "Study non-carbon compounds, including metals, salts, and minerals. Understand periodic trends and chemical bonding.",
          learningObjectives: [
            "Understand periodic trends",
            "Identify types of chemical bonds",
            "Predict compound properties",
            "Apply Lewis structures"
          ],
          prerequisites: ["Basic Chemistry", "Atomic Structure"],
          subtopics: [
            { title: "Periodic Table", deadline_minutes: 25 },
            { title: "Chemical Bonding", deadline_minutes: 20 }
          ],
          concepts: [
            {
              title: "Periodic Trends",
              explanation: "Patterns in properties of elements across the periodic table, including atomic radius, ionization energy, and electronegativity.",
              image: "https://images.unsplash.com/photo-1532187863486-abf9dbad1b69?w=400&h=300&fit=crop"
            },
            {
              title: "Chemical Bonding",
              explanation: "The attractive forces that hold atoms together in compounds, including ionic, covalent, and metallic bonds.",
              image: "https://images.unsplash.com/photo-1532187863486-abf9dbad1b69?w=400&h=300&fit=crop"
            }
          ],
          examples: [
            {
              title: "Ionic Bond Formation",
              description: "How sodium and chlorine form an ionic bond",
              code: "Na + Cl → Na⁺ + Cl⁻ → NaCl\nSodium loses 1 electron\nChlorine gains 1 electron",
              image: "https://images.unsplash.com/photo-1532187863486-abf9dbad1b69?w=400&h=300&fit=crop"
            }
          ],
          questions: [
            { 
              id: "chem-inorg-1",
              question: "What is the atomic number of carbon?", 
              type: "multiple_choice",
              options: [
                { text: "6", correct: true },
                { text: "12", correct: false },
                { text: "8", correct: false },
                { text: "14", correct: false }
              ]
            },
            { 
              id: "chem-inorg-2",
              question: "What type of bond forms between a metal and non-metal?", 
              type: "multiple_choice",
              options: [
                { text: "Ionic bond", correct: true },
                { text: "Covalent bond", correct: false },
                { text: "Metallic bond", correct: false },
                { text: "Hydrogen bond", correct: false }
              ]
            },
            { 
              id: "chem-inorg-3",
              question: "Explain the periodic trends in atomic radius", 
              type: "short_answer"
            }
          ]
        },
        {
          id: "chem-3",
          title: "Physical Chemistry",
          difficulty: "Advanced",
          duration: 60,
          description: "Apply physics principles to chemical systems. Study thermodynamics, kinetics, and quantum mechanics in chemistry.",
          learningObjectives: [
            "Apply thermodynamic principles to chemical reactions",
            "Understand reaction kinetics and rates",
            "Use quantum mechanical models",
            "Calculate equilibrium constants"
          ],
          prerequisites: ["Inorganic Chemistry", "Calculus", "Physics"],
          subtopics: [
            { title: "Thermodynamics", deadline_minutes: 30 },
            { title: "Kinetics", deadline_minutes: 30 }
          ],
          concepts: [
            {
              title: "Chemical Thermodynamics",
              explanation: "The study of energy changes in chemical reactions and the spontaneity of processes.",
              image: "https://images.unsplash.com/photo-1532187863486-abf9dbad1b69?w=400&h=300&fit=crop"
            },
            {
              title: "Reaction Kinetics",
              explanation: "The study of reaction rates and the factors that influence how fast chemical reactions occur.",
              image: "https://images.unsplash.com/photo-1532187863486-abf9dbad1b69?w=400&h=300&fit=crop"
            }
          ],
          examples: [
            {
              title: "Ideal Gas Law",
              description: "Calculate the volume of 1 mole of gas at STP",
              code: "PV = nRT\nV = nRT/P\nV = (1)(0.0821)(273)/1\nV = 22.4 L",
              image: "https://images.unsplash.com/photo-1532187863486-abf9dbad1b69?w=400&h=300&fit=crop"
            }
          ],
          questions: [
            { 
              id: "chem-phys-1",
              question: "What is the ideal gas law?", 
              type: "multiple_choice",
              options: [
                { text: "PV = nRT", correct: true },
                { text: "PV = nR", correct: false },
                { text: "P = nRT", correct: false },
                { text: "V = nRT", correct: false }
              ]
            },
            { 
              id: "chem-phys-2",
              question: "What is the rate law for a first-order reaction?", 
              type: "multiple_choice",
              options: [
                { text: "Rate = k[A]", correct: true },
                { text: "Rate = k[A]²", correct: false },
                { text: "Rate = k", correct: false },
                { text: "Rate = k[A][B]", correct: false }
              ]
            },
            { 
              id: "chem-phys-3",
              question: "Explain the concept of activation energy in chemical reactions", 
              type: "short_answer"
            }
          ]
        }
      ]
    };

    // Default topics if courseId not found
    const defaultTopics: TopicItem[] = [
      {
        id: "default-1",
        title: "Introduction to the Subject",
        difficulty: "Beginner",
        duration: 30,
        description: "Get started with the fundamental concepts and build a strong foundation.",
        learningObjectives: [
          "Understand basic concepts",
          "Learn fundamental principles",
          "Apply knowledge to simple problems"
        ],
        prerequisites: ["None"],
        subtopics: [
          { title: "Basic Concepts", deadline_minutes: 15 },
          { title: "Fundamentals", deadline_minutes: 15 }
        ],
        concepts: [
          {
            title: "Introduction",
            explanation: "Welcome to this comprehensive learning journey. We'll start with the basics and build up to advanced concepts.",
            image: "https://images.unsplash.com/photo-1509228468518-180dd4864904?w=400&h=300&fit=crop"
          }
        ],
        examples: [
          {
            title: "Getting Started",
            description: "Let's begin with a simple example to understand the concepts",
            code: "// Example code or formula\nresult = input + processing + output",
            image: "https://images.unsplash.com/photo-1509228468518-180dd4864904?w=400&h=300&fit=crop"
          }
        ],
        questions: [
          { 
            id: "default-1-1",
            question: "What is the main topic of this course?", 
            type: "short_answer"
          },
          { 
            id: "default-1-2",
            question: "What are the key learning objectives?", 
            type: "short_answer"
          }
        ]
      }
    ];

    return dummyTopicsMap[courseId] || defaultTopics;
  };

  // Function to create dynamic course using new_agent
  const createDynamicCourse = async (courseId: string) => {
    if (!user) return null;

    try {
      console.log("Creating dynamic course for courseId:", courseId);
      
      // Map courseId to subject and topic
      const courseMapping: { [key: string]: { subject: string; topic: string } } = {
        "1": { subject: "Mathematics", topic: "Advanced Mathematics" },
        "2": { subject: "Physics", topic: "Physics Fundamentals" },
        "3": { subject: "Chemistry", topic: "Chemistry Review" }
      };

      const courseInfo = courseMapping[courseId] || { subject: "General", topic: "Course" };
      
      const response = await dynamicCourseService.createCourseWithUser(
        courseInfo.subject,
        courseInfo.topic,
        "intermediate",
        4,
        user
      );

      console.log("Dynamic course created:", response);
      
      // Convert response to our format
      const dynamicTopics: TopicItem[] = response.curriculum.map((lesson: any) => ({
        id: lesson.id,
        title: lesson.title,
        difficulty: lesson.difficulty,
        duration: lesson.duration,
        subtopics: lesson.subtopics || [],
        questions: lesson.questions || []
      }));

      return {
        title: response.title,
        topics: dynamicTopics,
        isDynamic: true
      };
    } catch (error) {
      console.error("Error creating dynamic course:", error);
      return null;
    }
  };

  useEffect(() => {
    const load = async () => {
      if (!courseId || !user) return;
      setLoading(true);
      setError(null);
      try {
        // First try to create a dynamic course using new_agent
        console.log("Attempting to create dynamic course...");
        const dynamicCourse = await createDynamicCourse(courseId);
        
        if (dynamicCourse) {
          console.log("Dynamic course created successfully");
          setTitle(dynamicCourse.title);
          setTopics(dynamicCourse.topics);
          setIsDynamicCourse(true);
          setLoading(false);
          return;
        }

        // Fallback to existing agent service
        try {
          const course = await agentService.getCourse(courseId);
          setTitle(course?.learning_path?.title || 'Course');
          setTopics(
            (course?.curriculum || []).map((c: any) => ({
              id: c.id,
              title: c.title,
              difficulty: c.difficulty,
              duration: c.duration,
              subtopics: c.subtopics || [],
              questions: c.questions || [],
            }))
          );
          setIsDynamicCourse(false);
        } catch (e) {
          // Fallback to plan status if course is not found in store
          try {
            const status = await agentService.getLearningPlanStatus(user.id);
            const plan = status?.plans?.[courseId] || status;
            const curriculum = plan?.curriculum || [];
            setTitle(plan?.learning_path?.title || plan?.title || 'Course');
            setTopics(
              curriculum.map((c: any) => ({
                id: c.id,
                title: c.title,
                difficulty: c.difficulty,
                duration: c.duration,
                subtopics: c.subtopics || [],
                questions: c.questions || [],
              }))
            );
            setIsDynamicCourse(false);
          } catch (planError) {
            // If all API calls fail, use dummy data
            console.log("Using dummy topics for course:", courseId);
            const dummyTopics = getDummyTopics(courseId);
            const courseTitles: { [key: string]: string } = {
              "1": "Advanced Mathematics",
              "2": "Physics Fundamentals", 
              "3": "Chemistry Review"
            };
            setTitle(courseTitles[courseId] || `Course ${courseId}`);
            setTopics(dummyTopics);
            setIsDynamicCourse(false);
          }
        }
      } catch (e: any) {
        // If all else fails, use dummy data
        console.log("Using dummy topics due to error:", e?.message);
        const dummyTopics = getDummyTopics(courseId);
        const courseTitles: { [key: string]: string } = {
          "1": "Advanced Mathematics",
          "2": "Physics Fundamentals", 
          "3": "Chemistry Review"
        };
        setTitle(courseTitles[courseId] || `Course ${courseId}`);
        setTopics(dummyTopics);
        setIsDynamicCourse(false);
        setError(null); // Clear error since we're using dummy data
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [courseId, user]);

  const startLesson = async (lessonId: string) => {
    if (!user) return;
    
    // Find the lesson in topics
    const lesson = topics.find(t => t.id === lessonId);
    if (lesson) {
      setActiveLesson(lesson);
      setLessonProgress(0);
    }
    
    try {
      const session = await agentService.startLearningSession({ user_id: user.id, lesson_id: lessonId });
      console.log(`Session started: ${session.session_id}`);
    } catch (error) {
      console.log("Backend not available, using offline mode");
    }
  };

  const takeTest = () => {
    const questions = topics.flatMap((t) => t.questions || []);
    navigate(`/course/${courseId}/test`, { state: { questions } });
  };

  const continueCourse = () => {
    setShowSubtopics(true);
  };

  const viewSubtopics = (topic: TopicItem) => {
    setSelectedTopic(topic);
  };

  const startSubtopic = (topicId: string, subtopicTitle: string) => {
    alert(`Starting subtopic: ${subtopicTitle} from topic: ${topicId}`);
  };

  const takeTopicTest = (topic: TopicItem) => {
    if (topic.questions && topic.questions.length > 0) {
      navigate(`/course/${courseId}/test`, { state: { questions: topic.questions } });
    } else {
      alert("No questions available for this topic yet.");
    }
  };

  const askAI = () => {
    window.open("/ai-chat", "_blank");
  };

  const openNotes = () => {
    window.open("/notes", "_blank");
  };

  const nextLessonSection = () => {
    if (activeLesson) {
      setLessonProgress(prev => Math.min(prev + 1, 3)); // 0: overview, 1: concepts, 2: examples, 3: practice
    }
  };

  const prevLessonSection = () => {
    if (activeLesson) {
      setLessonProgress(prev => Math.max(prev - 1, 0));
    }
  };

  if (loading) return <div className="p-6">Loading...</div>;
  if (error) return <div className="p-6 text-red-500">{error}</div>;

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-semibold">{title}</h1>
          {isDynamicCourse && (
            <Badge variant="secondary" className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
              🤖 AI Generated
            </Badge>
          )}
        </div>
        <div className="flex gap-2">
          <Button 
            onClick={continueCourse}
            className="bg-green-600 text-white hover:bg-green-700"
          >
            Continue Course
          </Button>
          {!isDynamicCourse && (
            <Button 
              variant="outline" 
              onClick={async () => {
                setLoading(true);
                const dynamicCourse = await createDynamicCourse(courseId || "");
                if (dynamicCourse) {
                  setTitle(dynamicCourse.title);
                  setTopics(dynamicCourse.topics);
                  setIsDynamicCourse(true);
                }
                setLoading(false);
              }}
              className="bg-blue-50 text-blue-700 hover:bg-blue-100 dark:bg-blue-900 dark:text-blue-200"
            >
              🤖 Generate with AI
            </Button>
          )}
          <Button variant="outline" onClick={askAI}>Ask AI</Button>
          <Button variant="outline" onClick={takeTest}>Take Test</Button>
          <Button variant="outline" onClick={openNotes}>Take Notes</Button>
        </div>
      </div>
      <Separator />

      {/* Active Lesson Display */}
      {activeLesson && (
        <Card className="border-2 border-blue-200">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-xl">{activeLesson.title}</CardTitle>
              <Button variant="outline" onClick={() => setActiveLesson(null)}>
                Close Lesson
              </Button>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant="secondary">{activeLesson.difficulty}</Badge>
              <Badge variant="outline">{activeLesson.duration} mins</Badge>
              <div className="flex-1 bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300" 
                  style={{ width: `${(lessonProgress / 3) * 100}%` }}
                />
              </div>
              <span className="text-sm text-muted-foreground">
                {lessonProgress + 1}/4
              </span>
            </div>
          </CardHeader>
          <CardContent>
            {lessonProgress === 0 && (
              <div className="space-y-4">
                <div>
                  <h3 className="text-lg font-semibold mb-2">Description</h3>
                  <p className="text-muted-foreground">{activeLesson.description}</p>
                </div>
                
                {activeLesson.learningObjectives && (
                  <div>
                    <h3 className="text-lg font-semibold mb-2">Learning Objectives</h3>
                    <ul className="list-disc list-inside space-y-1">
                      {activeLesson.learningObjectives.map((objective, index) => (
                        <li key={index} className="text-muted-foreground">{objective}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {activeLesson.prerequisites && (
                  <div>
                    <h3 className="text-lg font-semibold mb-2">Prerequisites</h3>
                    <div className="flex flex-wrap gap-2">
                      {activeLesson.prerequisites.map((prereq, index) => (
                        <Badge key={index} variant="outline">{prereq}</Badge>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {lessonProgress === 1 && activeLesson.concepts && (
              <div className="space-y-4">
                <h3 className="text-lg font-semibold">Key Concepts</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {activeLesson.concepts.map((concept, index) => (
                    <div key={index} className="border rounded-lg p-4">
                      <h4 className="font-semibold mb-2">{concept.title}</h4>
                      <p className="text-muted-foreground mb-3">{concept.explanation}</p>
                      {concept.image && (
                        <img 
                          src={concept.image} 
                          alt={concept.title}
                          className="w-full h-32 object-cover rounded"
                        />
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {lessonProgress === 2 && activeLesson.examples && (
              <div className="space-y-4">
                <h3 className="text-lg font-semibold">Examples</h3>
                <div className="space-y-4">
                  {activeLesson.examples.map((example, index) => (
                    <div key={index} className="border rounded-lg p-4">
                      <h4 className="font-semibold mb-2">{example.title}</h4>
                      <p className="text-muted-foreground mb-3">{example.description}</p>
                      {example.code && (
                        <div className="bg-gray-100 dark:bg-gray-800 p-3 rounded font-mono text-sm mb-3">
                          <pre>{example.code}</pre>
                        </div>
                      )}
                      {example.image && (
                        <img 
                          src={example.image} 
                          alt={example.title}
                          className="w-full h-32 object-cover rounded"
                        />
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {lessonProgress === 3 && (
              <div className="space-y-4">
                <h3 className="text-lg font-semibold">Practice & Assessment</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Button 
                    onClick={() => takeTopicTest(activeLesson)}
                    className="h-20 text-lg"
                    disabled={!activeLesson.questions || activeLesson.questions.length === 0}
                  >
                    Take Quiz ({activeLesson.questions?.length || 0} questions)
                  </Button>
                  <Button 
                    variant="outline" 
                    className="h-20 text-lg"
                    onClick={() => setShowSubtopics(true)}
                  >
                    View Subtopics
                  </Button>
                </div>
              </div>
            )}

            <div className="flex justify-between mt-6">
              <Button 
                variant="outline" 
                onClick={prevLessonSection}
                disabled={lessonProgress === 0}
              >
                Previous
              </Button>
              <Button 
                onClick={nextLessonSection}
                disabled={lessonProgress === 3}
              >
                {lessonProgress === 3 ? "Complete" : "Next"}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Topics Covered</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {topics.length === 0 && (
              <div className="text-sm text-muted-foreground">No topics yet.</div>
            )}
            {topics.map((t) => (
              <div key={t.id} className="flex items-center justify-between border rounded-lg p-3">
                <div>
                  <div className="font-medium">{t.title}</div>
                  <div className="text-xs text-muted-foreground">Duration: {t.duration} mins</div>
                  {t.subtopics && t.subtopics.length > 0 && (
                    <div className="mt-1 text-xs text-muted-foreground">
                      Subtopics: {t.subtopics.map((s) => s.title).join(', ')}
                    </div>
                  )}
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant="secondary">{t.difficulty}</Badge>
                  <Button size="sm" onClick={() => startLesson(t.id)}>Start</Button>
                  {t.subtopics && t.subtopics.length > 0 && (
                    <Button size="sm" variant="outline" onClick={() => viewSubtopics(t)}>
                      View Subtopics
                    </Button>
                  )}
                  {t.questions && t.questions.length > 0 && (
                    <Button size="sm" variant="outline" onClick={() => takeTopicTest(t)}>
                      Test
                    </Button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {showSubtopics && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Course Subtopics</CardTitle>
              <Button variant="outline" onClick={() => setShowSubtopics(false)}>
                Close
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {topics.map((topic) => (
                <div key={topic.id} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="text-lg font-semibold">{topic.title}</h3>
                    <div className="flex items-center gap-2">
                      <Badge variant="secondary">{topic.difficulty}</Badge>
                      <Badge variant="outline">{topic.duration} mins</Badge>
                    </div>
                  </div>
                  
                  {topic.subtopics && topic.subtopics.length > 0 ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {topic.subtopics.map((subtopic, index) => (
                        <div key={index} className="border rounded-lg p-3 bg-gray-50 dark:bg-gray-800">
                          <div className="flex items-center justify-between">
                            <div>
                              <h4 className="font-medium">{subtopic.title}</h4>
                              <p className="text-sm text-muted-foreground">
                                Duration: {subtopic.deadline_minutes} minutes
                              </p>
                            </div>
                            <Button 
                              size="sm" 
                              onClick={() => startSubtopic(topic.id, subtopic.title)}
                              className="bg-blue-600 text-white hover:bg-blue-700"
                            >
                              Start
                            </Button>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-sm text-muted-foreground">
                      No subtopics available for this topic.
                    </div>
                  )}
                  
                  {topic.questions && topic.questions.length > 0 && (
                    <div className="mt-3 pt-3 border-t">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">
                          {topic.questions.length} questions available
                        </span>
                        <Button 
                          size="sm" 
                          variant="outline" 
                          onClick={() => takeTopicTest(topic)}
                        >
                          Take Test
                        </Button>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {selectedTopic && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>{selectedTopic.title} - Subtopics</CardTitle>
              <Button variant="outline" onClick={() => setSelectedTopic(null)}>
                Close
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {selectedTopic.subtopics && selectedTopic.subtopics.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {selectedTopic.subtopics.map((subtopic, index) => (
                  <div key={index} className="border rounded-lg p-4 bg-gray-50 dark:bg-gray-800">
                    <div className="flex items-center justify-between">
                      <div>
                        <h4 className="font-medium">{subtopic.title}</h4>
                        <p className="text-sm text-muted-foreground">
                          Duration: {subtopic.deadline_minutes} minutes
                        </p>
                      </div>
                      <Button 
                        size="sm" 
                        onClick={() => startSubtopic(selectedTopic.id, subtopic.title)}
                        className="bg-green-600 text-white hover:bg-green-700"
                      >
                        Start
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-sm text-muted-foreground">
                No subtopics available for this topic.
              </div>
            )}
          </CardContent>
        </Card>
      )}

      <Tabs defaultValue="ai">
        <TabsList>
          <TabsTrigger value="ai">Ask AI</TabsTrigger>
          <TabsTrigger value="test">Take Test</TabsTrigger>
          <TabsTrigger value="notes">Take Notes</TabsTrigger>
        </TabsList>
        
      </Tabs>
    </div>
  );
};

export default CoursePage;