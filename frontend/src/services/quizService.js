import axios from "axios";

const API = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL, // FastAPI backend
});

// Upload a YouTube link
export const generateQuizFromYouTube = async (youtubeUrl, targetLang = "en", difficulty = "medium") => {
  const formData = new FormData();
  formData.append("youtube_url", youtubeUrl);
  formData.append("target_lang", targetLang);
  formData.append("difficulty", difficulty);

  const response = await API.post("/youtube_link/", formData);
  return response.data;
};

// Upload a video file
export const generateQuizFromFile = async (file, targetLang = "en", difficulty = "medium") => {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("target_lang", targetLang);
  formData.append("difficulty", difficulty);

  const response = await API.post("/upload_file/", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
};
