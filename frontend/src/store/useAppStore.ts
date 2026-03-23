import { create } from "zustand";

export const useAppStore = create((set) => ({
  user: null,
  setUser: (user) => set({ user }),

  loading: false,
  setLoading: (loading) => set({ loading }),

  theme: "dark",
  toggleTheme: () =>
    set((s) => ({ theme: s.theme === "dark" ? "light" : "dark" })),
}));