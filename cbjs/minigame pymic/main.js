// Main JavaScript for Pymic Music

// Form validation
document.addEventListener('DOMContentLoaded', function() {
    // Add loading states to forms
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitButton = form.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.textContent = 'Loading...';
            }
        });
    });
});

// Audio player enhancements
function setupAudioPlayer() {
    const audioPlayer = document.getElementById('audioPlayer');
    if (audioPlayer) {
        // Add keyboard controls
        document.addEventListener('keydown', function(e) {
            if (e.code === 'Space' && document.activeElement.tagName !== 'INPUT') {
                e.preventDefault();
                if (audioPlayer.paused) {
                    audioPlayer.play();
                } else {
                    audioPlayer.pause();
                }
            }
        });
    }
}

setupAudioPlayer();

