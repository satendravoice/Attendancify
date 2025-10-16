// Matrix Rain Effect for Attendancify
// This script creates a fullscreen matrix code rain effect as background

document.addEventListener('DOMContentLoaded', function() {
    // Configuration variables
    const CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789$#@%&*";
    const FONT_SIZE = 14;
    const MIN_SPEED = 2;
    const MAX_SPEED = 8;
    const MIN_FADE = 0.02;
    const MAX_FADE = 0.05;
    const DENSITY = 0.97; // Probability of character change (higher = more flickering)
    
    // Create canvas element
    const canvas = document.createElement('canvas');
    canvas.id = 'matrix-canvas';
    const container = document.getElementById('matrix-background');
    container.appendChild(canvas);
    
    // Set canvas dimensions to match window
    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    
    // Set initial font
    ctx.font = `${FONT_SIZE}px monospace`;
    ctx.textBaseline = 'top';
    
    // Create columns array
    const columns = [];
    const columnCount = Math.floor(canvas.width / FONT_SIZE);
    
    // Initialize columns
    for (let i = 0; i < columnCount; i++) {
        columns.push({
            x: i * FONT_SIZE,
            y: Math.random() * -canvas.height,
            speed: MIN_SPEED + Math.random() * (MAX_SPEED - MIN_SPEED),
            chars: [],
            fadeRate: MIN_FADE + Math.random() * (MAX_FADE - MIN_FADE),
            length: 5 + Math.floor(Math.random() * 20)
        });
        
        // Initialize characters for this column
        for (let j = 0; j < columns[i].length; j++) {
            columns[i].chars.push({
                char: CHARS.charAt(Math.floor(Math.random() * CHARS.length)),
                opacity: Math.random()
            });
        }
    }
    
    // Draw function
    function draw() {
        // Semi-transparent black overlay to create fading effect - reduced opacity for better visibility
        ctx.fillStyle = 'rgba(0, 0, 0, 0.03)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        // Set text style
        ctx.font = `${FONT_SIZE}px monospace`;
        
        // Draw each column
        columns.forEach(column => {
            // Update column position
            column.y += column.speed;
            
            // Reset column if it goes well off screen (with buffer)
            if (column.y - column.length * FONT_SIZE > canvas.height + 200) {
                column.y = Math.random() * -200;
                column.speed = MIN_SPEED + Math.random() * (MAX_SPEED - MIN_SPEED);
                column.length = 5 + Math.floor(Math.random() * 20);
                
                // Reinitialize characters for this column
                column.chars = [];
                for (let j = 0; j < column.length; j++) {
                    column.chars.push({
                        char: CHARS.charAt(Math.floor(Math.random() * CHARS.length)),
                        opacity: Math.random()
                    });
                }
            }
            
            // Draw each character in the column
            for (let i = 0; i < column.length; i++) {
                const yPos = column.y - i * FONT_SIZE;
                
                // Only draw if character is on screen (with buffer)
                if (yPos > -200 && yPos < canvas.height + 100) {
                    // Randomly change character
                    if (Math.random() > DENSITY) {
                        column.chars[i].char = CHARS.charAt(Math.floor(Math.random() * CHARS.length));
                    }
                    
                    // Fade trail effect - head is brightest
                    const headOpacity = 0.8; // Reduced opacity for better visibility
                    const trailOpacity = Math.max(0, 1 - (i / column.length));
                    column.chars[i].opacity = i === 0 ? headOpacity : trailOpacity * 0.5; // Reduced trail opacity
                    
                    // Set color based on position in trail
                    if (i === 0) {
                        // Head character - bright green with reduced opacity
                        ctx.fillStyle = `rgba(0, 255, 0, ${column.chars[i].opacity * 0.7})`;
                    } else if (i < 3) {
                        // Near head - lighter green with reduced opacity
                        ctx.fillStyle = `rgba(0, 200, 0, ${column.chars[i].opacity * 0.5})`;
                    } else {
                        // Trail - darker green with reduced opacity
                        ctx.fillStyle = `rgba(0, 150, 0, ${column.chars[i].opacity * 0.3})`;
                    }
                    
                    // Draw character
                    ctx.fillText(column.chars[i].char, column.x, yPos);
                }
            }
        });
        
        // Continue animation loop
        requestAnimationFrame(draw);
    }
    
    // Start animation
    draw();
    
    // Handle window resize
    window.addEventListener('resize', () => {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    });
    
    // Handle theme changes (matrix only visible in dark mode)
    function updateVisibility() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        container.style.display = currentTheme === 'dark' ? 'block' : 'none';
    }
    
    // Initial visibility check
    updateVisibility();
    
    // Watch for theme changes
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'attributes' && mutation.attributeName === 'data-theme') {
                updateVisibility();
            }
        });
    });
    
    observer.observe(document.documentElement, {
        attributes: true
    });
});