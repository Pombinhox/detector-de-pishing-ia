document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    
    if (dropZone && fileInput) {
        dropZone.addEventListener('click', () => fileInput.click());

        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('dragover');
        });

        dropZone.addEventListener('dragleave', () => {
            dropZone.classList.remove('dragover');
        });

        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
            if (e.dataTransfer.files.length) {
                fileInput.files = e.dataTransfer.files;
                handleFileUpload(e.dataTransfer.files[0]);
            }
        });

        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length) {
                handleFileUpload(e.target.files[0]);
            }
        });
    }
});

let currentAnalysisId = null;

async function handleFileUpload(file) {
    if (!file.type.startsWith('image/')) {
        showError('Tipo de arquivo inválido', 'Por favor, envie uma imagem (PNG, JPG, WEBP, etc.)');
        return;
    }

    document.getElementById('dropZone').style.display = 'none';
    document.getElementById('loader').style.display = 'flex';
    document.getElementById('resultsArea').style.display = 'none';
    hideError();

    const formData = new FormData();
    formData.append('file', file);

    let response;
    try {
        response = await fetch('/api/analyze/image', {
            method: 'POST',
            body: formData
        });
    } catch (networkError) {
        // Falha de rede — servidor provavelmente não está rodando
        console.error('Erro de rede:', networkError);
        showError(
            'Erro de conexão com o servidor',
            `Não foi possível contactar /api/analyze/image. Verifique se o servidor FastAPI está rodando na porta 8000.\n\nDetalhe: ${networkError.message}`
        );
        resetScanner();
        return;
    }

    if (!response.ok) {
        let body = '';
        try { body = await response.text(); } catch (_) {}
        console.error('HTTP erro:', response.status, body);
        showError(
            `Erro do servidor (HTTP ${response.status})`,
            body || 'O servidor retornou um erro sem detalhes.'
        );
        resetScanner();
        return;
    }

    let data;
    try {
        data = await response.json();
    } catch (jsonError) {
        console.error('Erro ao parsear JSON:', jsonError);
        showError('Resposta inválida do servidor', `Não foi possível ler a resposta JSON.\n${jsonError.message}`);
        resetScanner();
        return;
    }

    try {
        currentAnalysisId = data.id;
        displayResults(data);
    } catch (renderError) {
        console.error('Erro ao exibir resultados:', renderError);
        showError(
            'Erro ao renderizar resultados',
            `A análise foi concluída mas houve um erro ao exibir os dados.\n\nDetalhe: ${renderError.message}\n\nStack: ${renderError.stack}`
        );
        resetScanner();
    }
}

function displayResults(data) {
    document.getElementById('loader').style.display = 'none';
    document.getElementById('resultsArea').style.display = 'block';

    // ── Score ──────────────────────────────────────────────────────────────
    const scoreEl = document.getElementById('resScore');
    scoreEl.innerText = `${Math.round(data.risk_score)}/100`;
    scoreEl.className = 'score-value ' + getScoreClass(data.risk_score);

    // ── Classification ─────────────────────────────────────────────────────
    const classEl = document.getElementById('resClass');
    classEl.innerText = data.classification;
    classEl.className = 'score-value ' + getScoreClass(data.risk_score);

    // ── AI Probability ─────────────────────────────────────────────────────
    const aiEl = document.getElementById('resAI');
    aiEl.innerText = data.ai_probability;
    aiEl.className = 'score-value ' + getAIProbClass(data.ai_probability);

    // ── HIDDEN CODES SECTION ───────────────────────────────────────────────
    const hiddenCodesSection = document.getElementById('hiddenCodesSection');
    const hiddenCodesList    = document.getElementById('hiddenCodesList');
    const noCodesSection     = document.getElementById('noCodesSection');
    const softwareTagContainer = document.getElementById('softwareTagContainer');
    const statsBlock         = document.getElementById('statsBlock');

    hiddenCodesList.innerHTML = '';

    const codes = data.hidden_codes || [];

    if (codes.length > 0) {
        hiddenCodesSection.style.display = 'block';
        noCodesSection.style.display = 'none';

        codes.forEach(code => {
            const div = document.createElement('div');
            div.className = 'code-badge';

            // Escolhe ícone baseado no prefixo
            let icon = '🔍';
            if (code.startsWith('🔴')) icon = '';
            else if (code.startsWith('📦')) icon = '';
            else if (code.startsWith('🏷️')) icon = '';
            else if (code.startsWith('📝')) icon = '';
            else if (code.startsWith('📄')) icon = '';
            else if (code.startsWith('🔏')) icon = '';
            else if (code.startsWith('📐')) icon = '';
            else if (code.startsWith('💻')) icon = '';
            else if (code.startsWith('⚠️')) icon = '';

            div.innerHTML = `<span class="badge-icon">${icon}</span><span>${escapeHtml(code)}</span>`;
            hiddenCodesList.appendChild(div);
        });

        // Anima entrada dos badges
        animateIn(hiddenCodesList.querySelectorAll('.code-badge'));

    } else {
        hiddenCodesSection.style.display = 'block';
        noCodesSection.style.display = 'block';
        // Mostra seção mas sem códigos
    }

    // ── Software Tag ───────────────────────────────────────────────────────
    const sw = data.metadata_software;
    if (sw && sw !== 'Nenhum' && sw !== 'None') {
        softwareTagContainer.style.display = 'block';
        document.getElementById('softwareTagText').innerText = sw;
        hiddenCodesSection.style.display = 'block';
    } else {
        softwareTagContainer.style.display = 'none';
    }

    // ── Statistical Analysis Bars ──────────────────────────────────────────
    const stats = data.statistical_analysis || {};
    if (stats && (stats.lsb_uniformity > 0 || stats.dct_score > 0)) {
        statsBlock.style.display = 'block';
        hiddenCodesSection.style.display = 'block';

        // Animate bars after a short delay for visual effect
        setTimeout(() => {
            const lsb = Math.min(stats.lsb_uniformity || 0, 100);
            const dct = Math.min(stats.dct_score || 0, 100);
            const lap = stats.laplacian_variance || 0;
            // Normalize laplacian to 0-100 (typical range 0-3000)
            const lapNorm = Math.min((lap / 3000) * 100, 100);

            setBar('lsbBar', 'lsbVal', lsb, lsb.toFixed(1) + '%');
            setBar('dctBar', 'dctVal', dct, dct.toFixed(1) + '%');
            setBar('lapBar', 'lapVal', lapNorm, lap.toFixed(0));
        }, 300);
    } else {
        statsBlock.style.display = 'none';
    }

    // ── Phishing Findings ──────────────────────────────────────────────────
    const pSection = document.getElementById('phishingSection');
    const pList    = document.getElementById('phishingList');
    pList.innerHTML = '';
    if (data.phishing_reasons && data.phishing_reasons.length > 0) {
        pSection.style.display = 'block';
        data.phishing_reasons.forEach(r => {
            const li = document.createElement('li');
            li.innerText = r;
            pList.appendChild(li);
        });
    } else {
        pSection.style.display = 'none';
    }

    // ── AI Indicator Reasons ───────────────────────────────────────────────
    const aSection = document.getElementById('aiSection');
    const aList    = document.getElementById('aiList');
    aList.innerHTML = '';
    // Filter out reasons already shown in hidden codes section
    const aiReasons = (data.ai_reasons || []).filter(r => !codes.includes(r));
    if (aiReasons.length > 0) {
        aSection.style.display = 'block';
        aiReasons.forEach(r => {
            const li = document.createElement('li');
            li.innerText = r;
            aList.appendChild(li);
        });
    } else {
        aSection.style.display = 'none';
    }
}

// ── Helpers ────────────────────────────────────────────────────────────────

function setBar(barId, valId, pct, label) {
    const bar = document.getElementById(barId);
    const val = document.getElementById(valId);
    if (bar) bar.style.width = pct + '%';
    if (val) val.innerText = label;
}

function animateIn(elements) {
    elements.forEach((el, i) => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(8px)';
        setTimeout(() => {
            el.style.transition = 'opacity 0.35s ease, transform 0.35s ease';
            el.style.opacity = '1';
            el.style.transform = 'translateY(0)';
        }, i * 60);
    });
}

function escapeHtml(str) {
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}

function getScoreClass(score) {
    if (score > 70) return 'status-danger';
    if (score > 30) return 'status-warning';
    return 'status-safe';
}

function getAIProbClass(prob) {
    if (prob === 'Alta') return 'status-danger';
    if (prob === 'Média') return 'status-warning';
    return 'status-safe';
}

function resetScanner() {
    document.getElementById('dropZone').style.display = 'block';
    document.getElementById('loader').style.display = 'none';
    document.getElementById('resultsArea').style.display = 'none';
    const fileInput = document.getElementById('fileInput');
    if (fileInput) fileInput.value = '';
    currentAnalysisId = null;
}

// ── Error Banner ───────────────────────────────────────────────────────────
function showError(title, detail) {
    let banner = document.getElementById('errorBanner');
    if (!banner) {
        banner = document.createElement('div');
        banner.id = 'errorBanner';
        banner.style.cssText = [
            'background: linear-gradient(135deg, rgba(239,68,68,0.12), rgba(185,28,28,0.08))',
            'border: 1px solid rgba(239,68,68,0.4)',
            'border-radius: 1rem',
            'padding: 1.2rem 1.4rem',
            'margin-top: 1.2rem',
            'color: #fca5a5',
            'font-size: 0.85rem',
            'line-height: 1.6',
            'white-space: pre-wrap',
            'word-break: break-all',
        ].join(';');
        // Insert after the drop zone inside the glass-card
        const card = document.querySelector('.glass-card');
        if (card) card.appendChild(banner);
    }
    banner.innerHTML = `<strong style="color:#f87171;font-size:0.95rem;">⚠️ ${escapeHtml(title)}</strong><br><br>${escapeHtml(detail)}`;
    banner.style.display = 'block';
}

function hideError() {
    const banner = document.getElementById('errorBanner');
    if (banner) banner.style.display = 'none';
}

function exportReport(format) {
    if (!currentAnalysisId) return;
    window.open(`/api/analyze/report/${currentAnalysisId}?format=${format}`, '_blank');
}
