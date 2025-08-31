import { create } from "zustand";

interface UIStoreState {
  darkMode: boolean;
  selectedQuizId: string | null;
  modalOpen: boolean;
}

interface UIStoreActions {
  setDarkMode: (value: boolean) => void;
  setSelectedQuizId: (id: string | null) => void;
  setModalOpen: (value: boolean) => void;
}

const useUIStore = create<UIStoreState & UIStoreActions>((set) => ({
  darkMode: false,
  setDarkMode: (value: boolean) => set({ darkMode: value }),

  selectedQuizId: null,
  setSelectedQuizId: (id: string | null) => set({ selectedQuizId: id }),

  modalOpen: false,
  setModalOpen: (value: boolean) => set({ modalOpen: value }),
}));

interface EditorState {
  code: string;
  setCode: (value: string) => void;
}

const useEditorStore = create<EditorState>((set) => ({
  code: "Enter your code here",
  setCode: (value: string) => set({ code: value }),
}));

export { useUIStore, useEditorStore };
