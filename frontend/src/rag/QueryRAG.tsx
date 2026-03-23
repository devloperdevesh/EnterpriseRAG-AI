import { sendQuery } from "../services/chatService";

const ask = async () => {
  const res = await sendQuery(query);
  setAnswer(res.data.answer);
};