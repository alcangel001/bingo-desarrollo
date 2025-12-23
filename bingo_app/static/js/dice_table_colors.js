// Sistema de colores dinámicos para la mesa de dados

const PRIZE_COLORS = {
    '2x': {
        primary: '#1e3a5f',
        secondary: '#2d4a6b',
        accent: '#4a90e2',
        glow: '#4a90e2',
        border: '#4a90e2',
        table: '#0f1e2e',
        text: '#ffffff',
        name: 'Clásico',
        intensity: 'low'
    },
    '3x': {
        primary: '#2d5016',
        secondary: '#3d6b1f',
        accent: '#5cb85c',
        glow: '#5cb85c',
        border: '#5cb85c',
        table: '#1a2e0f',
        text: '#ffffff',
        name: 'Verde',
        intensity: 'low'
    },
    '5x': {
        primary: '#4a2c1a',
        secondary: '#6b3d2d',
        accent: '#d4a574',
        glow: '#d4a574',
        border: '#d4a574',
        table: '#2e1a0f',
        text: '#ffffff',
        name: 'Dorado',
        intensity: 'medium'
    },
    '10x': {
        primary: '#5a1a3a',
        secondary: '#7a2a5a',
        accent: '#9b59b6',
        glow: '#9b59b6',
        border: '#9b59b6',
        table: '#3a0f2e',
        text: '#ffffff',
        name: 'Púrpura',
        intensity: 'medium'
    },
    '25x': {
        primary: '#3a1a0a',
        secondary: '#5a2a1a',
        accent: '#f39c12',
        glow: '#f39c12',
        border: '#f39c12',
        table: '#2e0f0a',
        text: '#ffffff',
        name: 'Naranja',
        intensity: 'high'
    },
    '100x': {
        primary: '#1a0a3a',
        secondary: '#2a1a5a',
        accent: '#00d4ff',
        glow: '#00d4ff',
        border: '#00d4ff',
        table: '#0f0a2e',
        text: '#ffffff',
        name: 'Eléctrico',
        intensity: 'very-high'
    },
    '500x': {
        primary: '#3a0a1a',
        secondary: '#5a1a2a',
        accent: '#ff0040',
        glow: '#ff0040',
        border: '#ff0040',
        table: '#2e0a0f',
        text: '#ffffff',
        name: 'Rojo Épico',
        intensity: 'very-high'
    },
    '1000x': {
        primary: '#1a0a0a',
        secondary: '#3a2a1a',
        accent: '#ffd700',
        glow: '#ffd700',
        border: '#ffd700',
        table: '#0f0a0a',
        text: '#ffd700',
        name: 'Leyenda',
        intensity: 'extreme'
    }
};

function applyPrizeColors(multiplier) {
    const colors = PRIZE_COLORS[multiplier] || PRIZE_COLORS['2x'];
    
    // Aplicar variables CSS
    document.documentElement.style.setProperty('--table-primary', colors.primary);
    document.documentElement.style.setProperty('--table-secondary', colors.secondary);
    document.documentElement.style.setProperty('--table-accent', colors.accent);
    document.documentElement.style.setProperty('--table-glow', colors.glow);
    document.documentElement.style.setProperty('--table-border', colors.border);
    document.documentElement.style.setProperty('--table-surface', colors.table);
    document.documentElement.style.setProperty('--table-text', colors.text);
    
    // Aplicar intensidad del brillo según el premio
    const tableSurface = document.getElementById('table-surface');
    if (tableSurface) {
        tableSurface.classList.remove('intense-glow', 'extreme-glow');
        
        if (colors.intensity === 'very-high' || colors.intensity === 'extreme') {
            tableSurface.classList.add('intense-glow');
        }
        
        if (colors.intensity === 'extreme') {
            tableSurface.classList.add('extreme-glow');
            createParticleEffect(colors.glow);
        }
    }
    
    // Efecto especial para premios grandes (100x+)
    if (parseInt(multiplier.replace('x', '')) >= 100) {
        document.body.classList.add('big-prize');
        
        if (colors.intensity !== 'extreme') {
            createParticleEffect(colors.glow);
        }
    } else {
        document.body.classList.remove('big-prize');
    }
    
    // Actualizar color de los avatares y elementos
    updatePlayerElementsColor(colors.accent);
    
    console.log(`🎨 Colores aplicados: ${colors.name} (${multiplier}) - Borde: ${colors.border}`);
}

function updatePlayerElementsColor(accentColor) {
    // Actualizar color de los bordes de avatares
    const avatars = document.querySelectorAll('.player-avatar');
    avatars.forEach(avatar => {
        avatar.style.borderColor = accentColor;
        avatar.style.boxShadow = `0 0 20px ${accentColor}`;
    });
    
    // Actualizar color de los dados
    const diceElements = document.querySelectorAll('.player-dice');
    diceElements.forEach(dice => {
        dice.style.borderColor = accentColor;
        dice.style.boxShadow = `0 0 20px ${accentColor}`;
    });
    
    // Actualizar color del botón de lanzar
    const rollBtn = document.getElementById('roll-dice-btn');
    if (rollBtn) {
        rollBtn.style.borderColor = accentColor;
        rollBtn.style.boxShadow = `0 0 30px ${accentColor}`;
    }
}

function createParticleEffect(color) {
    const container = document.getElementById('table-container');
    if (!container) return;
    
    for (let i = 0; i < 20; i++) {
        const particle = document.createElement('div');
        particle.className = 'prize-particle';
        particle.style.cssText = `
            position: absolute;
            width: 10px;
            height: 10px;
            background: ${color};
            border-radius: 50%;
            pointer-events: none;
            opacity: 0.8;
            left: ${Math.random() * 100}%;
            top: ${Math.random() * 100}%;
            animation: floatParticle 3s ease-in-out infinite;
            animation-delay: ${Math.random() * 2}s;
            box-shadow: 0 0 20px ${color};
            z-index: 100;
        `;
        container.appendChild(particle);
        
        setTimeout(() => particle.remove(), 3000);
    }
}

// CSS para partículas y efectos adicionales
const style = document.createElement('style');
style.textContent = `
    @keyframes floatParticle {
        0%, 100% {
            transform: translateY(0) scale(1);
            opacity: 0.8;
        }
        50% {
            transform: translateY(-50px) scale(1.5);
            opacity: 0.3;
        }
    }
    
    .extreme-glow {
        position: relative;
    }
    
    .extreme-glow::before {
        content: '';
        position: absolute;
        top: -20px;
        left: -20px;
        right: -20px;
        bottom: -20px;
        border-radius: 50%;
        border: 4px solid var(--table-border);
        opacity: 0.6;
        animation: outerGlow 2s ease-in-out infinite;
        pointer-events: none;
    }
    
    .extreme-glow::after {
        content: '';
        position: absolute;
        top: -40px;
        left: -40px;
        right: -40px;
        bottom: -40px;
        border-radius: 50%;
        border: 2px solid var(--table-border);
        opacity: 0.4;
        animation: outerGlow 3s ease-in-out infinite;
        animation-delay: 0.5s;
        pointer-events: none;
    }
    
    @keyframes outerGlow {
        0%, 100% {
            opacity: 0.4;
            transform: scale(1);
        }
        50% {
            opacity: 0.8;
            transform: scale(1.05);
        }
    }
    
    .big-prize .table-surface {
        position: relative;
    }
    
    .big-prize .table-surface::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        border-radius: 50%;
        border: 2px solid var(--table-border);
        transform: translate(-50%, -50%);
        animation: ripple 2s ease-out infinite;
        pointer-events: none;
    }
    
    @keyframes ripple {
        0% {
            width: 0;
            height: 0;
            opacity: 1;
        }
        100% {
            width: 800px;
            height: 800px;
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

