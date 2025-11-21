export interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  imageUrl?: string;
  timestamp: Date;
}

export interface SessionInfo {
  session_id: string;
  welcome_info: string;
  item_names: string[];
  status: string;
}

export interface ChatResponse {
  user_input: string;
  bot_response: string;
  status: string;
}

export interface ItemSubmitResponse {
  user_info: string;
  response_info: string;
  status: string;
  image_base64?: string;
}

export interface ImageUploadResponse {
  user_info: string;
  response: string;
  status: string;
  display_image_base64?: string;
}
