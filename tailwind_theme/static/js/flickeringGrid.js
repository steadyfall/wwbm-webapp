function createGrid() {
    const grid = document.getElementById('smooth-grid');
    grid.innerHTML = ''; // Clear existing grid
    const gridSize = Math.ceil(window.innerWidth / 24) * Math.ceil(window.innerHeight / 24);

    for (let i = 0; i < gridSize; i++) {
        const square = document.createElement('div');
        square.classList.add('grid-square', 'absolute', 'bg-blue-500');
        square.style.opacity = Math.random() * 0.5;
        grid.appendChild(square);
    }
}

function positionGrid() {
    const squares = document.querySelectorAll('.grid-square');
    const gridWidth = Math.ceil(window.innerWidth / 24);

    squares.forEach((square, index) => {
        const row = Math.floor(index / gridWidth);
        const col = index % gridWidth;
        square.style.left = `${col * 24}px`;
        square.style.top = `${row * 24}px`;
    });
}

function animateGrid() {
    const squares = document.querySelectorAll('.grid-square');
    squares.forEach(square => {
        const targetOpacity = Math.random() * 0.5;
        square.style.opacity = targetOpacity;
    });
}

function handleResize() {
    createGrid();
    positionGrid();
}

createGrid();
positionGrid();
setInterval(animateGrid, 1000); // Smooth animation every 2 seconds

window.addEventListener('resize', handleResize);
