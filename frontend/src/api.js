import axios from "axios";

const API = axios.create({
  baseURL: "http://127.0.0.1:8000", // FastAPI backend URL
});

export const getStatus = () => API.get("/status");
export const createDPP = (data) => API.post("/dpp", data);
