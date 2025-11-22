import { useNavigate } from 'react-router-dom';
import './LevelSelect.css';

interface Level {
  id: string;
  title: string;
  description: string;
  icon: string;
  configPath: string;
  difficulty: '简单' | '中等' | '困难';
  estimatedTime: string;
}

const LevelSelect = () => {
  const navigate = useNavigate();

  const levels: Level[] = [
    {
      id: 'police',
      title: '刑侦大队',
      description: '调查发生在朝阳市内的连环凶杀案，通过线索分析找出真凶',
      icon: '🕵️‍♂️',
      configPath: 'config/police.yaml',
      difficulty: '中等',
      estimatedTime: '15-20分钟'
    },
    {
      id: 'taoist',
      title: '修仙问道',
      description: '跟随道士学习修仙之道，收集五行灵物筑基炼丹',
      icon: '🧙‍♂️',
      configPath: 'config/taoist.yaml',
      difficulty: '简单',
      estimatedTime: '10-15分钟'
    }
  ];

  const startGame = (level: Level) => {
    const sessionId = `session_${Date.now()}_${level.id}`;
    navigate('/chat', {
      state: {
        sessionId,
        levelConfig: level.configPath,
        levelTitle: level.title
      }
    });
  };

  const goBack = () => {
    navigate('/');
  };

  return (
    <div className="level-select-container">
      <div className="level-select-header">
        <button className="back-button" onClick={goBack}>
          ←
        </button>
        <h1 className="level-select-title">选择关卡</h1>
      </div>

      <div className="level-grid">
        {levels.map((level) => (
          <div key={level.id} className="level-card" onClick={() => startGame(level)}>
            <div className="level-icon">{level.icon}</div>
            <div className="level-info">
              <h3 className="level-name">{level.title}</h3>
              <p className="level-description">{level.description}</p>
              <div className="level-meta">
                <span className={`level-difficulty ${level.difficulty.toLowerCase()}`}>
                  {level.difficulty}
                </span>
                <span className="level-time">{level.estimatedTime}</span>
              </div>
            </div>
            <div className="level-arrow">▶</div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default LevelSelect;