import { api } from "../api/client";

export const uploadDoc = (file: any) => {
  const formData = new FormData();
  formData.append("file", file);

  return api.post("/documents/upload", formData);
};