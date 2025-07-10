/**
 * AIMER PRO - Application JavaScript
 * © 2025 - Interface web moderne avec Detectron2
 */

class AimerApp {
    constructor() {
        this.socket = null;
        this.currentUser = null;
        this.detectionActive = false;
        this.videoStream = null;
        this.currentTab = 'datasets';

        // Éléments DOM
        this.elements = {};

        // Données en temps réel
        this.hardwareData = null;
        this.detectionResults = [];

        this.init();
    }

    init() {
        this.initElements();
        this.initSocketIO();
        this.initEventListeners();
        this.loadInitialData();
        this.startHardwareMonitoring();

        console.log('AIMER PRO initialisé');
        this.showNotification('AIMER PRO démarré', 'success');
    }

    initElements() {
        // Récupérer tous les éléments DOM nécessaires
        this.elements = {
            // Header
            systemStatus: document.getElementById('systemStatus'),
            systemStatusText: document.getElementById('systemStatusText'),
            userLevel: document.getElementById('userLevel'),
            levelProgress: document.getElementById('levelProgress'),
            userXP: document.getElementById('userXP'),
            loginBtn: document.getElementById('loginBtn'),

            // Hardware
            cpuUsage: document.getElementById('cpuUsage'),
            ramUsage: document.getElementById('ramUsage'),
            gpuUsage: document.getElementById('gpuUsage'),
            cpuTemp: document.getElementById('cpuTemp'),
            aiScore: document.getElementById('aiScore'),
            aiScoreText: document.getElementById('aiScoreText'),

            // Performance
            fpsCounter: document.getElementById('fpsCounter'),
            detectionCount: document.getElementById('detectionCount'),
            processTime: document.getElementById('processTime'),
            modelName: document.getElementById('modelName'),

            // User Progress
            currentLevel: document.getElementById('currentLevel'),
            currentXP: document.getElementById('currentXP'),
            badgeCount: document.getElementById('badgeCount'),
            userRank: document.getElementById('userRank'),

            // Video
            videoSource: document.getElementById('videoSource'),
            videoElement: document.getElementById('videoElement'),
            detectionCanvas: document.getElementById('detectionCanvas'),
            detectionOverlay: document.getElementById('detectionOverlay'),
            detectionStatus: document.getElementById('detectionStatus'),
            detectionStatusText: document.getElementById('detectionStatusText'),
            startDetectionBtn: document.getElementById('startDetectionBtn'),
            stopDetectionBtn: document.getElementById('stopDetectionBtn'),

            // Controls
            confidenceSlider: document.getElementById('confidenceSlider'),
            confidenceValue: document.getElementById('confidenceValue'),
            visualizationMode: document.getElementById('visualizationMode'),
            screenshotBtn: document.getElementById('screenshotBtn'),
            recordBtn: document.getElementById('recordBtn'),

            // Results
            detectionResults: document.getElementById('detectionResults'),
            recentBadges: document.getElementById('recentBadges'),
            leaderboard: document.getElementById('leaderboard'),

            // Modal
            loginModal: document.getElementById('loginModal'),
            usernameInput: document.getElementById('usernameInput'),
            loginSubmitBtn: document.getElementById('loginSubmitBtn'),
            loginCancelBtn: document.getElementById('loginCancelBtn'),

            // Tabs
            tabContent: document.getElementById('tabContent'),

            // Quick Actions
            quickDetectBtn: document.getElementById('quickDetectBtn'),
            quickTrainBtn: document.getElementById('quickTrainBtn'),
            quickDatasetBtn: document.getElementById('quickDatasetBtn')
        };
    }

    initSocketIO() {
        this.socket = io();

        this.socket.on('connect', () => {
            console.log('Connecté au serveur');
            this.updateSystemStatus('online');
            this.showNotification('Connecté au serveur', 'success');
        });

        this.socket.on('disconnect', () => {
            console.log('Déconnecté du serveur');
            this.updateSystemStatus('offline');
            this.showNotification('Connexion perdue', 'error');
        });

        this.socket.on('hardware_update', (data) => {
            this.updateHardwareDisplay(data);
        });

        this.socket.on('detection_results', (data) => {
            this.updateDetectionResults(data);
        });

        this.socket.on('detection_stream_started', () => {
            this.detectionActive = true;
            this.updateDetectionStatus('online');
        });

        this.socket.on('detection_stream_stopped', () => {
            this.detectionActive = false;
            this.updateDetectionStatus('offline');
        });
    }

    initEventListeners() {
        // Login
        this.elements.loginBtn.addEventListener('click', () => this.showLoginModal());
        this.elements.loginSubmitBtn.addEventListener('click', () => this.handleLogin());
        this.elements.loginCancelBtn.addEventListener('click', () => this.hideLoginModal());

        // Detection
        this.elements.startDetectionBtn.addEventListener('click', () => this.startDetection());
        this.elements.stopDetectionBtn.addEventListener('click', () => this.stopDetection());

        // Video source
        this.elements.videoSource.addEventListener('change', () => this.handleVideoSourceChange());

        // Controls
        this.elements.confidenceSlider.addEventListener('input', (e) => {
            const value = Math.round(e.target.value * 100);
            this.elements.confidenceValue.textContent = `${value}%`;
        });

        // Quick actions
        this.elements.quickDetectBtn.addEventListener('click', () => this.quickDetection());
        this.elements.quickTrainBtn.addEventListener('click', () => this.quickTraining());
        this.elements.quickDatasetBtn.addEventListener('click', () => this.showTab('datasets'));

        // Screenshot
        this.elements.screenshotBtn.addEventListener('click', () => this.takeScreenshot());

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => this.handleKeyboard(e));
    }

    async loadInitialData() {
        try {
            // Charger les données hardware
            await this.loadHardwareData();

            // Charger le leaderboard
            await this.loadLeaderboard();

            // Afficher l'onglet par défaut
            this.showTab('datasets');

        } catch (error) {
            console.error('Erreur chargement données:', error);
            this.showNotification('Erreur de chargement', 'error');
        }
    }

    async loadHardwareData() {
        try {
            const response = await fetch('/api/hardware');
            const data = await response.json();
            this.hardwareData = data;
            this.updateHardwareDisplay(data);
        } catch (error) {
            console.error('Erreur hardware:', error);
        }
    }

    async loadLeaderboard() {
        try {
            const response = await fetch('/api/leaderboard');
            const data = await response.json();
            this.updateLeaderboard(data);
        } catch (error) {
            console.error('Erreur leaderboard:', error);
        }
    }

    startHardwareMonitoring() {
        // Demander des mises à jour hardware toutes les 2 secondes
        setInterval(() => {
            if (this.socket && this.socket.connected) {
                this.socket.emit('request_hardware_update');
            }
        }, 2000);
    }

    updateSystemStatus(status) {
        const statusElement = this.elements.systemStatus;
        const textElement = this.elements.systemStatusText;

        statusElement.className = `status-indicator status-${status}`;

        switch (status) {
            case 'online':
                textElement.textContent = 'Système En Ligne';
                break;
            case 'offline':
                textElement.textContent = 'Système Hors Ligne';
                break;
            case 'warning':
                textElement.textContent = 'Système Dégradé';
                break;
        }
    }

    updateDetectionStatus(status) {
        const statusElement = this.elements.detectionStatus;
        const textElement = this.elements.detectionStatusText;

        statusElement.className = `status-indicator status-${status}`;

        switch (status) {
            case 'online':
                textElement.textContent = 'Détection Active';
                break;
            case 'offline':
                textElement.textContent = 'Arrêté';
                break;
            case 'warning':
                textElement.textContent = 'Erreur';
                break;
        }
    }

    updateHardwareDisplay(data) {
        if (!data) return;

        try {
            // CPU
            if (data.cpu) {
                this.elements.cpuUsage.textContent = `${data.cpu.usage.overall.toFixed(1)}%`;
                if (data.cpu.temperature) {
                    this.elements.cpuTemp.textContent = `${data.cpu.temperature.toFixed(1)}°C`;
                }
            }

            // RAM
            if (data.memory && data.memory.virtual) {
                this.elements.ramUsage.textContent = `${data.memory.virtual.percentage.toFixed(1)}%`;
            }

            // GPU
            if (data.gpu && data.gpu.gpus && data.gpu.gpus.length > 0) {
                const gpu = data.gpu.gpus[0];
                this.elements.gpuUsage.textContent = `${gpu.load.toFixed(1)}%`;
            } else {
                this.elements.gpuUsage.textContent = 'N/A';
            }

            // Score IA
            if (data.performance) {
                const score = data.performance.overall_score || 0;
                this.elements.aiScore.style.width = `${score}%`;
                this.elements.aiScoreText.textContent = `${score.toFixed(0)}%`;

                // Couleur selon le score
                if (score > 80) {
                    this.elements.aiScore.className = 'bg-green-500 h-2 rounded-full';
                } else if (score > 60) {
                    this.elements.aiScore.className = 'bg-yellow-500 h-2 rounded-full';
                } else {
                    this.elements.aiScore.className = 'bg-red-500 h-2 rounded-full';
                }
            }

        } catch (error) {
            console.error('Erreur mise à jour hardware:', error);
        }
    }

    updateDetectionResults(data) {
        if (!data || !data.results) return;

        try {
            // Mettre à jour les stats
            this.elements.detectionCount.textContent = data.results.length;
            if (data.fps) {
                this.elements.fpsCounter.textContent = data.fps.toFixed(1);
            }

            // Afficher les résultats
            const container = this.elements.detectionResults;
            container.innerHTML = '';

            if (data.results.length === 0) {
                container.innerHTML = '<div class="text-gray-500 text-sm text-center py-4">Aucune détection</div>';
                return;
            }

            data.results.forEach((result, index) => {
                const resultDiv = document.createElement('div');
                resultDiv.className = 'bg-gray-800 p-3 rounded border border-gray-600';
                resultDiv.innerHTML = `
                    <div class="flex items-center justify-between mb-2">
                        <span class="font-semibold">${result.class}</span>
                        <span class="text-sm text-gray-400">${(result.confidence * 100).toFixed(1)}%</span>
                    </div>
                    <div class="text-xs text-gray-500">
                        Position: ${result.bbox[0].toFixed(0)}, ${result.bbox[1].toFixed(0)}<br>
                        Taille: ${(result.bbox[2] - result.bbox[0]).toFixed(0)}x${(result.bbox[3] - result.bbox[1]).toFixed(0)}
                    </div>
                `;
                container.appendChild(resultDiv);
            });

            // Dessiner les détections sur le canvas
            this.drawDetections(data.results);

        } catch (error) {
            console.error('Erreur mise à jour détections:', error);
        }
    }

    drawDetections(results) {
        const canvas = this.elements.detectionCanvas;
        const video = this.elements.videoElement;

        if (!canvas || !video) return;

        const ctx = canvas.getContext('2d');

        // Ajuster la taille du canvas
        canvas.width = video.videoWidth || video.clientWidth;
        canvas.height = video.videoHeight || video.clientHeight;

        // Effacer le canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Couleurs pour les classes
        const colors = [
            '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
            '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9'
        ];

        results.forEach((result, index) => {
            const [x1, y1, x2, y2] = result.bbox;
            const color = colors[index % colors.length];

            // Mode de visualisation
            const mode = this.elements.visualizationMode.value;

            if (mode === 'bbox' || mode === 'mask') {
                // Dessiner le rectangle
                ctx.strokeStyle = color;
                ctx.lineWidth = 2;
                ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);

                // Dessiner le label
                const label = `${result.class} (${(result.confidence * 100).toFixed(1)}%)`;
                ctx.font = '14px Arial';
                const textWidth = ctx.measureText(label).width;

                // Background du label
                ctx.fillStyle = color;
                ctx.fillRect(x1, y1 - 25, textWidth + 10, 25);

                // Texte du label
                ctx.fillStyle = 'white';
                ctx.fillText(label, x1 + 5, y1 - 5);
            }

            if (mode === 'panoptic') {
                // Mode "Vision IA" avec effet spécial
                ctx.strokeStyle = color;
                ctx.lineWidth = 3;
                ctx.setLineDash([5, 5]);
                ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);
                ctx.setLineDash([]);

                // Effet glow
                ctx.shadowColor = color;
                ctx.shadowBlur = 10;
                ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);
                ctx.shadowBlur = 0;
            }
        });
    }

    updateLeaderboard(data) {
        const container = this.elements.leaderboard;
        container.innerHTML = '';

        if (!data || data.length === 0) {
            container.innerHTML = '<div class="text-gray-500 text-sm text-center py-4">Aucun joueur</div>';
            return;
        }

        data.forEach((player, index) => {
            const playerDiv = document.createElement('div');
            playerDiv.className = 'flex items-center justify-between p-2 rounded bg-gray-800';

            let rankColor = 'text-gray-400';
            if (index === 0) rankColor = 'text-yellow-400';
            else if (index === 1) rankColor = 'text-gray-300';
            else if (index === 2) rankColor = 'text-orange-400';

            playerDiv.innerHTML = `
                <div class="flex items-center space-x-2">
                    <span class="${rankColor} font-bold">#${player.rank}</span>
                    <span class="text-sm">${player.username}</span>
                </div>
                <div class="text-xs text-gray-400">
                    Lvl ${player.level} • ${player.total_xp} XP
                </div>
            `;

            container.appendChild(playerDiv);
        });
    }

    showLoginModal() {
        this.elements.loginModal.classList.remove('hidden');
        this.elements.usernameInput.focus();
    }

    hideLoginModal() {
        this.elements.loginModal.classList.add('hidden');
        this.elements.usernameInput.value = '';
    }

    async handleLogin() {
        const username = this.elements.usernameInput.value.trim();

        if (!username) {
            this.showNotification('Veuillez entrer un nom d\'utilisateur', 'error');
            return;
        }

        try {
            const response = await fetch('/api/user/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username })
            });

            const data = await response.json();

            if (data.success) {
                this.currentUser = data.profile;
                this.updateUserDisplay();
                this.hideLoginModal();
                this.showNotification(`Bienvenue ${username}!`, 'success');

                // Recharger le leaderboard
                await this.loadLeaderboard();
            } else {
                this.showNotification('Erreur de connexion', 'error');
            }

        } catch (error) {
            console.error('Erreur login:', error);
            this.showNotification('Erreur de connexion', 'error');
        }
    }

    updateUserDisplay() {
        if (!this.currentUser) return;

        // Header
        this.elements.userLevel.textContent = this.currentUser.level;
        this.elements.userXP.textContent = this.currentUser.xp;

        // Progress bar
        const xpNeeded = this.currentUser.level * 100;
        const progress = (this.currentUser.xp / xpNeeded) * 100;
        this.elements.levelProgress.style.width = `${progress}%`;

        // User progress panel
        this.elements.currentLevel.textContent = this.currentUser.level;
        this.elements.currentXP.textContent = this.currentUser.total_xp;
        this.elements.badgeCount.textContent = this.currentUser.badges.length;

        // Login button
        this.elements.loginBtn.innerHTML = `<i class="fas fa-user mr-2"></i>${this.currentUser.username}`;

        // Update badges
        this.updateBadgesDisplay();
    }

    updateBadgesDisplay() {
        if (!this.currentUser || !this.currentUser.badges) return;

        const container = this.elements.recentBadges;
        container.innerHTML = '';

        if (this.currentUser.badges.length === 0) {
            container.innerHTML = '<div class="text-gray-500 text-sm text-center py-4">Aucun badge</div>';
            return;
        }

        // Afficher les 3 derniers badges
        const recentBadges = this.currentUser.badges.slice(0, 3);

        recentBadges.forEach(badge => {
            const badgeDiv = document.createElement('div');
            badgeDiv.className = 'flex items-center space-x-2 p-2 bg-gray-800 rounded';
            badgeDiv.innerHTML = `
                <span class="text-2xl">${badge.icon}</span>
                <div>
                    <div class="font-semibold text-sm">${badge.name}</div>
                    <div class="text-xs text-gray-400">${badge.description}</div>
                </div>
            `;
            container.appendChild(badgeDiv);
        });
    }

    async startDetection() {
        try {
            const source = this.elements.videoSource.value;

            if (!source) {
                this.showNotification('Veuillez sélectionner une source vidéo', 'error');
                return;
            }

            // Démarrer la source vidéo
            await this.startVideoSource(source);

            // Démarrer la détection
            const response = await fetch('/api/detection/start', {
                method: 'POST'
            });

            if (response.ok) {
                this.socket.emit('start_detection_stream');
                this.showNotification('Détection démarrée', 'success');
            }

        } catch (error) {
            console.error('Erreur démarrage détection:', error);
            this.showNotification('Erreur de démarrage', 'error');
        }
    }

    async stopDetection() {
        try {
            this.socket.emit('stop_detection_stream');

            await fetch('/api/detection/stop', {
                method: 'POST'
            });

            // Arrêter la vidéo
            if (this.videoStream) {
                this.videoStream.getTracks().forEach(track => track.stop());
                this.videoStream = null;
                this.elements.videoElement.srcObject = null;
            }

            this.showNotification('Détection arrêtée', 'info');

        } catch (error) {
            console.error('Erreur arrêt détection:', error);
        }
    }

    async startVideoSource(source) {
        try {
            if (source === 'webcam') {
                this.videoStream = await navigator.mediaDevices.getUserMedia({
                    video: { width: 640, height: 480 },
                    audio: false
                });
                this.elements.videoElement.srcObject = this.videoStream;
            } else if (source === 'screen') {
                this.videoStream = await navigator.mediaDevices.getDisplayMedia({
                    video: { width: 1280, height: 720 },
                    audio: false
                });
                this.elements.videoElement.srcObject = this.videoStream;
            }
        } catch (error) {
            console.error('Erreur source vidéo:', error);
            this.showNotification('Impossible d\'accéder à la source vidéo', 'error');
        }
    }

    handleVideoSourceChange() {
        // Arrêter la détection si active
        if (this.detectionActive) {
            this.stopDetection();
        }
    }

    quickDetection() {
        this.elements.videoSource.value = 'webcam';
        this.startDetection();
    }

    quickTraining() {
        this.showTab('training');
        this.showNotification('Module d\'entraînement', 'info');
    }

    takeScreenshot() {
        const video = this.elements.videoElement;
        const canvas = document.createElement('canvas');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;

        const ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0);

        // Télécharger l'image
        const link = document.createElement('a');
        link.download = `aimer_screenshot_${Date.now()}.png`;
        link.href = canvas.toDataURL();
        link.click();

        this.showNotification('Capture d\'écran sauvegardée', 'success');
    }

    handleKeyboard(event) {
        // Raccourcis clavier
        if (event.ctrlKey) {
            switch (event.key) {
                case 's':
                    event.preventDefault();
                    this.takeScreenshot();
                    break;
                case 'd':
                    event.preventDefault();
                    if (this.detectionActive) {
                        this.stopDetection();
                    } else {
                        this.quickDetection();
                    }
                    break;
            }
        }
    }

    showTab(tabName) {
        this.currentTab = tabName;

        // Mettre à jour les boutons
        document.querySelectorAll('.tab-button').forEach(btn => {
            btn.classList.remove('border-blue-500', 'text-blue-400');
            btn.classList.add('border-transparent', 'text-gray-400');
        });

        // Activer le bon bouton
        const activeBtn = document.querySelector(`[onclick="showTab('${tabName}')"]`);
        if (activeBtn) {
            activeBtn.classList.remove('border-transparent', 'text-gray-400');
            activeBtn.classList.add('border-blue-500', 'text-blue-400');
        }

        // Charger le contenu
        this.loadTabContent(tabName);
    }

    async loadTabContent(tabName) {
        const container = this.elements.tabContent;

        switch (tabName) {
            case 'datasets':
                container.innerHTML = await this.getDatasetContent();
                break;
            case 'training':
                container.innerHTML = this.getTrainingContent();
                break;
            case 'cheats':
                container.innerHTML = this.getCheatsContent();
                break;
            case 'analytics':
                container.innerHTML = this.getAnalyticsContent();
                break;
        }
    }

    async getDatasetContent() {
        try {
            const response = await fetch('/api/datasets/popular');
            const datasets = await response.json();

            let html = `
                <div class="hardware-card p-6 rounded-lg">
                    <h3 class="text-xl font-bold mb-4">Gestionnaire de Datasets</h3>
                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            `;

            Object.entries(datasets).forEach(([key, dataset]) => {
                html += `
                    <div class="border border-gray-600 rounded-lg p-4 card-hover">
                        <h4 class="font-semibold mb-2">${dataset.name}</h4>
                        <p class="text-sm text-gray-400 mb-3">${dataset.description}</p>
                        <div class="text-xs text-gray-500 mb-3">
                            <div>Taille: ${dataset.size}</div>
                            <div>Images: ${dataset.num_images.toLocaleString()}</div>
                            <div>Classes: ${dataset.num_classes}</div>
                        </div>
                        <button class="w-full bg-blue-600 hover:bg-blue-700 px-3 py-2 rounded text-sm">
                            <i class="fas fa-download mr-2"></i>Télécharger
                        </button>
                    </div>
                `;
            });

            html += `
                    </div>
                </div>
            `;

            return html;

        } catch (error) {
            return '<div class="text-red-400">Erreur de chargement des datasets</div>';
        }
    }

    getTrainingContent() {
        return `
            <div class="hardware-card p-6 rounded-lg">
                <h3 class="text-xl font-bold mb-4">Entraînement de Modèles</h3>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                        <h4 class="font-semibold mb-3">Nouveau Modèle</h4>
                        <div class="space-y-4">
                            <div>
                                <label class="block text-sm font-medium mb-2">Nom du modèle</label>
                                <input type="text" class="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2" placeholder="Mon modèle Detectron2">
                            </div>
                            <div>
                                <label class="block text-sm font-medium mb-2">Dataset</label>
                                <select class="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2">
                                    <option>COCO 2017</option>
                                    <option>Custom Dataset</option>
                                </select>
                            </div>
                            <div>
                                <label class="block text-sm font-medium mb-2">Architecture</label>
                                <select class="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2">
                                    <option>Faster R-CNN</option>
                                    <option>Mask R-CNN</option>
                                    <option>RetinaNet</option>
                                </select>
                            </div>
                            <button class="w-full bg-green-600 hover:bg-green-700 py-2 rounded">
                                <i class="fas fa-play mr-2"></i>Commencer l'entraînement
                            </button>
                        </div>
                    </div>
                    <div>
                        <h4 class="font-semibold mb-3">Modèles Existants</h4>
                        <div class="space-y-2">
                            <div class="border border-gray-600 rounded p-3">
                                <div class="flex justify-between items-center">
                                    <span>Detectron2_COCO</span>
                                    <span class="text-sm text-green-400">Prêt</span>
                                </div>
                                <div class="text-xs text-gray-400">Précision: 89.2% • Vitesse: 15 FPS</div>
                            </div>
                            <div class="border border-gray-600 rounded p-3">
                                <div class="flex justify-between items-center">
                                    <span>Custom_Model_001</span>
                                    <span class="text-sm text-yellow-400">Entraînement...</span>
                                </div>
                                <div class="text-xs text-gray-400">Époque: 45/100 • Perte: 0.234</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    getCheatsContent() {
        return `
            <div class="hardware-card p-6 rounded-lg">
                <h3 class="text-xl font-bold mb-4">Vision Cheats Generator</h3>
                <div class="grid grid-cols-1 md:
