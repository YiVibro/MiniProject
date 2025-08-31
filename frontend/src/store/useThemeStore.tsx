import { create } from "zustand";

interface ThemeState {
  theme: string;
  setTheme: (theme: string) => void;
}

export const useThemeStore = create<ThemeState>((set) => ({
  theme: "light",
  setTheme: (theme) => {
    document.documentElement.setAttribute("data-theme", theme);
    set({ theme });
  },
}));

// Apply theme on load
const saved = localStorage.getItem("theme") || "light";
document.documentElement.setAttribute("data-theme", saved);
useThemeStore.setState({ theme: saved });
