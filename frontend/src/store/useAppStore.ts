import { create } from "zustand";

type AppState = {
  user: any;
  setUser: (user: any) => void;

  sidebarOpen: boolean;
  toggleSidebar: () => void;

  loading: boolean;
  setLoading: (val: boolean) => void;
};

export const useAppStore = create<AppState>((set) => ({
  user: null,
  setUser: (user) => set({ user }),

  sidebarOpen: true,
  toggleSidebar: () =>
    set((state) => ({ sidebarOpen: !state.sidebarOpen })),

  loading: false,
  setLoading: (val) => set({ loading: val }),
}));