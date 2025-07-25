// JavaScript customizado para POPPFIRE ADMIN
// Evita que o menu lateral recolha automaticamente

document.addEventListener('DOMContentLoaded', function() {
    console.log('POPPFIRE Admin: Carregando customizações...');
    
    // Desabilitar colapso automático do sidebar
    function disableSidebarCollapse() {
        // Remove classes que causam o colapso
        const body = document.body;
        const sidebar = document.querySelector('.main-sidebar');
        
        if (body && sidebar) {
            // Força o sidebar a permanecer aberto
            body.classList.remove('sidebar-collapse');
            body.classList.add('sidebar-fixed');
            
            // Remove event listeners que causam colapso
            const sidebarToggle = document.querySelector('[data-widget="pushmenu"]');
            if (sidebarToggle) {
                // Clona o elemento para remover todos os event listeners
                const newToggle = sidebarToggle.cloneNode(true);
                sidebarToggle.parentNode.replaceChild(newToggle, sidebarToggle);
            }
            
            console.log('POPPFIRE Admin: Colapso do sidebar desabilitado');
        }
    }
    
    // Executar ao carregar a página
    disableSidebarCollapse();
    
    // Observador para detectar mudanças e reforçar as configurações
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
                const target = mutation.target;
                
                // Se o body tentar adicionar sidebar-collapse, remove
                if (target === document.body && target.classList.contains('sidebar-collapse')) {
                    target.classList.remove('sidebar-collapse');
                    console.log('POPPFIRE Admin: Impedido colapso automático');
                }
            }
        });
    });
    
    // Observar mudanças no body
    observer.observe(document.body, {
        attributes: true,
        attributeFilter: ['class']
    });
    
    // Reforçar configurações a cada 1 segundo por 10 segundos
    let attempts = 0;
    const interval = setInterval(function() {
        attempts++;
        disableSidebarCollapse();
        
        if (attempts >= 10) {
            clearInterval(interval);
            console.log('POPPFIRE Admin: Configurações finalizadas');
        }
    }, 1000);
    
    // Prevenir colapso em links do menu
    const menuLinks = document.querySelectorAll('.nav-sidebar .nav-link');
    menuLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            // Não impede a navegação, apenas mantém o sidebar aberto
            setTimeout(function() {
                document.body.classList.remove('sidebar-collapse');
            }, 100);
        });
    });
    
    console.log('POPPFIRE Admin: Customizações carregadas com sucesso');
});
