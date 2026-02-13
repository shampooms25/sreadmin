// Script JavaScript para ser incluído no portal captive (index.html)
// Registra a visualização do vídeo quando o usuário assiste

(function() {
    'use strict';
    
    // Configuração
    const API_URL = 'https://paineleld.poppnet.com.br/api/captive-portal/success/';
    const VIDEO_ELEMENT_ID = 'captive-video'; // ID do elemento <video>
    
    /**
     * Obtém o username do formulário de login ou URL
     */
    function getUsername() {
        // Tentar obter do formulário
        const usernameInput = document.querySelector('input[name="auth_user"], input[name="username"]');
        if (usernameInput && usernameInput.value) {
            return usernameInput.value;
        }
        
        // Tentar obter da URL (query parameter)
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get('username') || urlParams.get('user') || 'anonymous';
    }
    
    /**
     * Obtém o nome do vídeo sendo reproduzido
     */
    function getVideoName() {
        const videoElement = document.getElementById(VIDEO_ELEMENT_ID) || document.querySelector('video');
        if (videoElement && videoElement.currentSrc) {
            // Extrair apenas o nome do arquivo da URL
            return videoElement.currentSrc.split('/').pop().split('?')[0];
        }
        return 'unknown.mp4';
    }
    
    /**
     * Formata a data/hora atual no formato esperado pela API
     */
    function getCurrentTimestamp() {
        const now = new Date();
        const year = now.getFullYear();
        const month = String(now.getMonth() + 1).padStart(2, '0');
        const day = String(now.getDate()).padStart(2, '0');
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        const seconds = String(now.getSeconds()).padStart(2, '0');
        
        return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
    }
    
    /**
     * Registra a visualização na API
     */
    function registerVideoView() {
        const username = getUsername();
        const video = getVideoName();
        const timestamp = getCurrentTimestamp();
        
        const payload = {
            username: username,
            video: video,
            origin: 'captive_portal',
            timestamp: timestamp
        };
        
        console.log('[Captive Portal] Registrando visualização:', payload);
        
        // Usar fetch API (moderno)
        fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload),
            mode: 'cors'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log('[Captive Portal] Visualização registrada com sucesso:', data);
            } else {
                console.error('[Captive Portal] Erro ao registrar visualização:', data);
            }
        })
        .catch(error => {
            console.error('[Captive Portal] Erro de conexão:', error);
        });
    }
    
    /**
     * Configura o listener no vídeo
     */
    function setupVideoListener() {
        const videoElement = document.getElementById(VIDEO_ELEMENT_ID) || document.querySelector('video');
        
        if (!videoElement) {
            console.warn('[Captive Portal] Elemento de vídeo não encontrado');
            return;
        }
        
        // Registrar quando o vídeo terminar
        videoElement.addEventListener('ended', function() {
            console.log('[Captive Portal] Vídeo finalizado, registrando visualização...');
            registerVideoView();
        });
        
        // Registrar se o vídeo for assistido por pelo menos 80%
        videoElement.addEventListener('timeupdate', function() {
            const percentWatched = (videoElement.currentTime / videoElement.duration) * 100;
            
            // Verificar se já foi registrado
            if (!videoElement.dataset.viewRegistered && percentWatched >= 80) {
                videoElement.dataset.viewRegistered = 'true';
                console.log('[Captive Portal] Vídeo assistido 80%, registrando visualização...');
                registerVideoView();
            }
        });
        
        console.log('[Captive Portal] Listeners configurados no vídeo');
    }
    
    // Inicializar quando o DOM estiver pronto
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', setupVideoListener);
    } else {
        setupVideoListener();
    }
    
})();
