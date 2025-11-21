import { useNavigate } from 'react-router-dom';
import './Home.css';

const Home = () => {
  const navigate = useNavigate();

  const startGame = () => {
    const sessionId = `session_${Date.now()}`;
    navigate('/chat', { state: { sessionId } });
  };

  return (
    <div className="home-container">
      <div className="home-content">
        <div className="logo-section">
          <div className="logo">🐋</div>
          <h1 className="title">鲸娱秘境</h1>
          <p className="subtitle">Whale Land VLM</p>
        </div>

        <div className="description">
          <p>MLLM结合线下密室的人工智能创新应用</p>
          <p className="description-detail">
            通过AI对话和图像识别，沉浸式体验密室解谜
          </p>
        </div>

        <div className="features">
          <div className="feature-item">
            <span className="feature-icon">💬</span>
            <span>智能对话</span>
          </div>
          <div className="feature-item">
            <span className="feature-icon">📷</span>
            <span>图像识别</span>
          </div>
          <div className="feature-item">
            <span className="feature-icon">🎭</span>
            <span>角色扮演</span>
          </div>
        </div>

        <button className="start-button" onClick={startGame}>
          开始游戏
        </button>

        <div className="footer">
          <p>欢迎大家在点评搜索"鲸娱秘境"</p>
          <p className="footer-note">线上demo为游戏环节一部分，并加入多模态元素</p>
        </div>
      </div>
    </div>
  );
};

export default Home;
