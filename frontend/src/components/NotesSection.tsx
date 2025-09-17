import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Plus, Search, Edit, Trash2, Brain, User, BookOpen } from "lucide-react";
import { motion } from "framer-motion";

interface Note {
  id: string;
  title: string;
  content: string;
  type: 'personal' | 'ai';
  subject: string;
  createdAt: Date;
  tags: string[];
}

export const NotesSection = () => {
  const [notes, setNotes] = useState<Note[]>([
    { id: '1', title: 'Quadratic Equations - Key Concepts', content: 'A quadratic equation is a polynomial equation of degree 2...', type: 'ai', subject: 'Mathematics', createdAt: new Date('2024-01-10'), tags: ['algebra','equations','formulas'] },
    { id: '2', title: 'Physics Study Session Notes', content: 'Newton\'s laws of motion...', type: 'personal', subject: 'Physics', createdAt: new Date('2024-01-12'), tags: ['newton','laws','motion'] },
    { id: '3', title: 'Chemical Bonding Summary', content: 'Chemical bonds are forces that hold atoms together...', type: 'ai', subject: 'Chemistry', createdAt: new Date('2024-01-15'), tags: ['bonding','ionic','covalent'] }
  ]);

  const [searchTerm, setSearchTerm] = useState("");
  const [selectedNote, setSelectedNote] = useState<Note | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [newNote, setNewNote] = useState({ title: '', content: '', subject: '', tags: '' });

  const personalNotes = notes.filter(n => n.type === 'personal');
  const aiNotes = notes.filter(n => n.type === 'ai');

  const filteredNotes = (list: Note[]) => list.filter(n => n.title.toLowerCase().includes(searchTerm.toLowerCase()) || n.content.toLowerCase().includes(searchTerm.toLowerCase()) || n.subject.toLowerCase().includes(searchTerm.toLowerCase()));

  const handleCreateNote = () => {
    const note: Note = { id: Date.now().toString(), title: newNote.title, content: newNote.content, type: 'personal', subject: newNote.subject, createdAt: new Date(), tags: newNote.tags.split(',').map(t => t.trim()).filter(t => t) };
    setNotes([note, ...notes]);
    setNewNote({ title: '', content: '', subject: '', tags: '' });
    setIsCreating(false);
    setSelectedNote(note);
  };

  const generateAINote = () => {
    const aiNote: Note = { id: Date.now().toString(), title: 'AI-Generated Study Summary', content: 'This is a simulated AI-generated note...', type: 'ai', subject: 'General', createdAt: new Date(), tags: ['ai-generated','summary'] };
    setNotes([aiNote, ...notes]);
    setSelectedNote(aiNote);
  };

  // Framer Motion Variants
  const fadeUp = { hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0, transition: { duration: 0.4 } } };
  const staggerContainer = { hidden: {}, visible: { transition: { staggerChildren: 0.1 } } };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2"><BookOpen className="w-8 h-8 text-blue-500"/>Study Notes</h1>
          <p className="text-gray-400">Organize your personal notes and AI-generated content</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={generateAINote} className="gap-2"><Brain className="w-4 h-4"/>Generate AI Note</Button>
          <Button onClick={() => setIsCreating(true)} className="gap-2"><Plus className="w-4 h-4"/>New Note</Button>
        </div>
      </div>

      <div className="grid lg:grid-cols-4 gap-6">
        {/* Left: Notes List */}
        <div className="lg:col-span-1">
          <Card className="h-[600px] flex flex-col">
            <CardHeader className="pb-3 px-4">
              <div className="relative">
                <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"/>
                <Input placeholder="Search notes..." value={searchTerm} onChange={e => setSearchTerm(e.target.value)} className="pl-9"/>
              </div>
            </CardHeader>
            <CardContent className="p-0 flex-1">
              <Tabs defaultValue="all" className="w-full h-full flex flex-col">
                <TabsList className="grid w-full grid-cols-3  mb-4">
                  <TabsTrigger value="all" className="text-xs">All</TabsTrigger>
                  <TabsTrigger value="personal" className="text-xs">Personal</TabsTrigger>
                  <TabsTrigger value="ai" className="text-xs">AI Notes</TabsTrigger>
                </TabsList>

                <ScrollArea className="flex-1">
                  {['all','personal','ai'].map((tab) => {
                    const list = tab==='all'?filteredNotes(notes) : tab==='personal'?filteredNotes(personalNotes) : filteredNotes(aiNotes);
                    return (
                      <TabsContent key={tab} value={tab} className="space-y-2 px-4">
                        <motion.div initial="hidden" animate="visible" variants={staggerContainer}>
                          {list.map(note => (
                            <motion.div key={note.id} className={`p-3 rounded-lg border cursor-pointer transition-colors hover:bg-gray-700/50 ${selectedNote?.id===note.id?'bg-blue-500/10 border-blue-500':''}`} onClick={() => setSelectedNote(note)} variants={fadeUp}>
                              <div className="flex items-start gap-2 mb-2">
                                {note.type==='ai'?<Brain className="w-4 h-4 text-blue-500 mt-1"/>:<User className="w-4 h-4 text-green-500 mt-1"/>}
                                <div className="flex-1 min-w-0">
                                  <h4 className="text-sm font-medium line-clamp-2">{note.title}</h4>
                                  <p className="text-xs text-gray-400 line-clamp-2 mt-1">{note.content}</p>
                                </div>
                              </div>
                              <div className="flex items-center justify-between">
                                <Badge variant="outline" className="text-xs">{note.subject}</Badge>
                                <span className="text-xs text-gray-400">{note.createdAt.toLocaleDateString()}</span>
                              </div>
                            </motion.div>
                          ))}
                        </motion.div>
                      </TabsContent>
                    )
                  })}
                </ScrollArea>
              </Tabs>
            </CardContent>
          </Card>
        </div>

        {/* Right: Selected Note / Create */}
        <div className="lg:col-span-3">
          <Card className="h-[600px] flex flex-col">
            <motion.div key={selectedNote?.id || 'new'} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }} className="flex-1 flex flex-col">
              {isCreating ? (
                <>
                  <CardHeader><CardTitle>Create New Note</CardTitle></CardHeader>
                  <CardContent className="flex-1 space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <label className="text-sm font-medium">Title</label>
                        <Input placeholder="Note title..." value={newNote.title} onChange={e => setNewNote({...newNote,title:e.target.value})}/>
                      </div>
                      <div className="space-y-2">
                        <label className="text-sm font-medium">Subject</label>
                        <Input placeholder="Subject..." value={newNote.subject} onChange={e => setNewNote({...newNote,subject:e.target.value})}/>
                      </div>
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Tags</label>
                      <Input placeholder="tag1, tag2..." value={newNote.tags} onChange={e => setNewNote({...newNote,tags:e.target.value})}/>
                    </div>
                    <div className="space-y-2 flex-1">
                      <label className="text-sm font-medium">Content</label>
                      <Textarea placeholder="Write note..." value={newNote.content} onChange={e => setNewNote({...newNote,content:e.target.value})} className="h-[300px] resize-none"/>
                    </div>
                    <div className="flex gap-2">
                      <Button onClick={handleCreateNote} disabled={!newNote.title || !newNote.content}>Save Note</Button>
                      <Button variant="outline" onClick={()=>setIsCreating(false)}>Cancel</Button>
                    </div>
                  </CardContent>
                </>
              ) : selectedNote ? (
                <>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        {selectedNote.type==='ai'?<Brain className="w-5 h-5 text-blue-500"/>:<User className="w-5 h-5 text-green-500"/>}
                        <div>
                          <CardTitle>{selectedNote.title}</CardTitle>
                          <div className="flex items-center gap-2 mt-1">
                            <Badge variant="outline">{selectedNote.subject}</Badge>
                            <span className="text-sm text-gray-400">{selectedNote.createdAt.toLocaleDateString()}</span>
                          </div>
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <Button variant="outline" size="sm"><Edit className="w-4 h-4"/></Button>
                        <Button variant="outline" size="sm"><Trash2 className="w-4 h-4"/></Button>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="flex-1 overflow-hidden">
                    <ScrollArea className="h-[400px] pr-4">
                      <div className="prose prose-sm max-w-none">
                        <p className="whitespace-pre-wrap">{selectedNote.content}</p>
                      </div>
                    </ScrollArea>
                    {selectedNote.tags.length>0 && (
                      <div className="mt-4 pt-4 border-t flex flex-wrap items-center gap-2">
                        <span className="text-sm font-medium">Tags:</span>
                        {selectedNote.tags.map((tag,i)=><Badge key={i} variant="secondary" className="text-xs">{tag}</Badge>)}
                      </div>
                    )}
                  </CardContent>
                </>
              ) : (
                <CardContent className="flex-1 flex flex-col items-center justify-center text-center text-muted-foreground">
                  <BookOpen className="w-12 h-12 mx-auto mb-4 opacity-50"/>
                  <p>Select a note to view or create a new one</p>
                </CardContent>
              )}
            </motion.div>
          </Card>
        </div>
      </div>
    </div>
  );
};
