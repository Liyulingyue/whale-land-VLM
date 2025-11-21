import { useState, useEffect, useRef } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Camera, Send, Image as ImageIcon, ArrowLeft, RotateCcw } from 'lucide-react';
import { gameService } from '../services/api';
import type { Message } from '../types';
import './Chat.css';

const Chat = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const sessionId = location.state?.sessionId || `session_${Date.now()}`;
  
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [welcomeInfo, setWelcomeInfo] = useState('');
  const [status, setStatus] = useState('');
  const [showCamera, setShowCamera] = useState(false);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    initSession();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const initSession = async () => {
    try {
      const sessionInfo = await gameService.createSession(sessionId);
      setWelcomeInfo(sessionInfo.welcome_info);
      setStatus(sessionInfo.status);
      
      // 添加欢迎消息
      const welcomeMessage: Message = {
        id: `msg_${Date.now()}`,
        type: 'assistant',
        content: sessionInfo.welcome_info,
        timestamp: new Date(),
      };
      setMessages([welcomeMessage]);
    } catch (error) {
      console.error('Failed to initialize session:', error);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = async () => {
    if (!inputText.trim() || isLoading) return;

    const userMessage: Message = {
      id: `msg_${Date.now()}`,
      type: 'user',
      content: inputText,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsLoading(true);

    try {
      const response = await gameService.sendMessage(sessionId, inputText);
      
      const botMessage: Message = {
        id: `msg_${Date.now()}_bot`,
        type: 'assistant',
        content: response.bot_response,
        timestamp: new Date(),
      };
      
      setMessages(prev => [...prev, botMessage]);
      setStatus(response.status);
    } catch (error) {
      console.error('Failed to send message:', error);
      const errorMessage: Message = {
        id: `msg_${Date.now()}_error`,
        type: 'assistant',
        content: '抱歉，消息发送失败，请重试。',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleImageUpload = async (file: File) => {
    const userMessage: Message = {
      id: `msg_${Date.now()}`,
      type: 'user',
      content: '发送了一张图片',
      imageUrl: URL.createObjectURL(file),
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await gameService.uploadImage(sessionId, file);
      
      const botMessage: Message = {
        id: `msg_${Date.now()}_bot`,
        type: 'assistant',
        content: response.response,
        timestamp: new Date(),
      };
      
      setMessages(prev => [...prev, botMessage]);
      setStatus(response.status);
    } catch (error) {
      console.error('Failed to upload image:', error);
      const errorMessage: Message = {
        id: `msg_${Date.now()}_error`,
        type: 'assistant',
        content: '抱歉，图片上传失败，请重试。',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file && file.type.startsWith('image/')) {
      handleImageUpload(file);
    }
  };

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { facingMode: 'environment' } 
      });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        setShowCamera(true);
      }
    } catch (error) {
      console.error('Failed to start camera:', error);
      alert('无法访问相机，请检查权限设置');
    }
  };

  const stopCamera = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const stream = videoRef.current.srcObject as MediaStream;
      stream.getTracks().forEach(track => track.stop());
      videoRef.current.srcObject = null;
      setShowCamera(false);
    }
  };

  const capturePhoto = () => {
    if (videoRef.current && canvasRef.current) {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const ctx = canvas.getContext('2d');
      if (ctx) {
        ctx.drawImage(video, 0, 0);
        canvas.toBlob((blob) => {
          if (blob) {
            const file = new File([blob], 'camera-photo.jpg', { type: 'image/jpeg' });
            handleImageUpload(file);
            stopCamera();
          }
        }, 'image/jpeg');
      }
    }
  };

  const handleReset = async () => {
    if (confirm('确定要重置游戏吗？')) {
      try {
        const sessionInfo = await gameService.resetSession(sessionId);
        setMessages([{
          id: `msg_${Date.now()}`,
          type: 'assistant',
          content: sessionInfo.welcome_info,
          timestamp: new Date(),
        }]);
        setStatus(sessionInfo.status);
      } catch (error) {
        console.error('Failed to reset session:', error);
      }
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <button className="back-button" onClick={() => navigate('/')}>
          <ArrowLeft size={20} />
        </button>
        <div className="header-title">
          <h2>🐋 鲸娱秘境</h2>
          <p className="session-status">{status}</p>
        </div>
        <button className="reset-button" onClick={handleReset}>
          <RotateCcw size={20} />
        </button>
      </div>

      <div className="messages-container">
        {messages.map((message) => (
          <div key={message.id} className={`message ${message.type}`}>
            <div className="message-content">
              {message.imageUrl && (
                <img src={message.imageUrl} alt="上传的图片" className="message-image" />
              )}
              <p>{message.content}</p>
            </div>
            <span className="message-time">
              {message.timestamp.toLocaleTimeString('zh-CN', { 
                hour: '2-digit', 
                minute: '2-digit' 
              })}
            </span>
          </div>
        ))}
        {isLoading && (
          <div className="message assistant">
            <div className="message-content typing">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {showCamera && (
        <div className="camera-modal">
          <div className="camera-content">
            <video ref={videoRef} autoPlay playsInline className="camera-preview" />
            <canvas ref={canvasRef} style={{ display: 'none' }} />
            <div className="camera-controls">
              <button className="camera-cancel" onClick={stopCamera}>
                取消
              </button>
              <button className="camera-capture" onClick={capturePhoto}>
                拍照
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="input-container">
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          style={{ display: 'none' }}
          onChange={handleFileSelect}
        />
        
        <button 
          className="action-button"
          onClick={() => fileInputRef.current?.click()}
          disabled={isLoading}
        >
          <ImageIcon size={20} />
        </button>
        
        <button 
          className="action-button"
          onClick={startCamera}
          disabled={isLoading}
        >
          <Camera size={20} />
        </button>

        <input
          type="text"
          className="message-input"
          placeholder="输入消息..."
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
          disabled={isLoading}
        />

        <button
          className="send-button"
          onClick={handleSendMessage}
          disabled={isLoading || !inputText.trim()}
        >
          <Send size={20} />
        </button>
      </div>
    </div>
  );
};

export default Chat;
