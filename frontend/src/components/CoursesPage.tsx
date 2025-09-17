import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { BookOpen, TrendingUp } from "lucide-react";
import { motion } from "framer-motion";

export const CoursesPage = () => {
  const courses = [
    {
      id: 1,
      title: "Advanced Mathematics",
      subject: "Mathematics",
      progress: 75,
      description: "Master calculus, linear algebra, and advanced mathematical concepts",
      lessons: 24,
      completedLessons: 18
    },
    {
      id: 2,
      title: "Physics Fundamentals",
      subject: "Physics",
      progress: 45,
      description: "Understand the fundamental principles of physics and their applications",
      lessons: 20,
      completedLessons: 9
    },
    {
      id: 3,
      title: "Chemistry Review",
      subject: "Chemistry",
      progress: 90,
      description: "Comprehensive review of organic and inorganic chemistry",
      lessons: 16,
      completedLessons: 14
    }
  ];

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2 text-foreground">
            <BookOpen className="w-8 h-8 text-primary" />
            My Courses
          </h1>
          <p className="text-muted-foreground">Track your learning progress and continue your studies</p>
        </div>
      </div>

      <motion.div 
        className="grid md:grid-cols-2 lg:grid-cols-3 gap-6"
        initial="hidden"
        animate="visible"
        variants={{
          hidden: {},
          visible: {
            transition: {
              staggerChildren: 0.1
            }
          }
        }}
      >
        {courses.map((course, index) => (
          <motion.div
            key={course.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1, duration: 0.4 }}
            whileHover={{ scale: 1.03 }}
          >
            <Card key={course.id} className="hover:shadow-lg transition-shadow h-full flex flex-col">
              <CardHeader className="hover:opacity-95 transition-opacity">
                <CardTitle>{course.title}</CardTitle>
                <div className="flex items-center justify-between">
                  <motion.span 
                    className="text-sm text-muted-foreground"
                    whileHover={{ opacity: 1 }}
                  >
                    {course.subject}
                  </motion.span>
                  <div className="flex items-center gap-1 text-sm text-primary">
                    <TrendingUp className="w-4 h-4" />
                    {course.progress}%
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-4 flex flex-col justify-between flex-1">
                <p className="text-sm text-muted-foreground">{course.description}</p>
                
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Progress</span>
                    <span>{course.completedLessons}/{course.lessons} lessons</span>
                  </div>
                  <motion.div 
                    className="w-full bg-muted rounded-full h-2 overflow-hidden"
                    initial={{ width: 0 }}
                    animate={{ width: "100%" }}
                    transition={{ duration: 0.8 }}
                  >
                    <motion.div 
                      className="bg-primary h-2 rounded-full"
                      initial={{ width: 0 }}
                      animate={{ width: `${course.progress}%` }}
                      transition={{ duration: 1.2, ease: "easeInOut" }}
                    />
                  </motion.div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </motion.div>
    </div>
  );
};
