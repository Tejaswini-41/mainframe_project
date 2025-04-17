const express = require('express');
const router = express.Router();

// In-memory database (will be replaced with DB2 later)
let users = [
    { id: 1, name: 'tejaswini' },
    { id: 2, name: 'arya' }
];

// GET all users
router.get('/', (req, res) => {
    res.json(users);
});

// GET user by ID
router.get('/:id', (req, res) => {
    const id = parseInt(req.params.id);
    const user = users.find(user => user.id === id);
    
    if (!user) {
        return res.status(404).json({ message: 'User not found' });
    }
    
    res.json(user);
});

// POST create new user
router.post('/', (req, res) => {
    const { name } = req.body;
    
    if (!name || !name.trim()) {
        return res.status(400).json({ message: 'Name is required' });
    }
    
    // Generate a new ID (in a real DB, this would be handled by the database)
    const id = users.length > 0 ? Math.max(...users.map(user => user.id)) + 1 : 1;
    
    const newUser = { id, name };
    users.push(newUser);
    
    res.status(201).json(newUser);
});

// PUT update user
router.put('/:id', (req, res) => {
    const id = parseInt(req.params.id);
    const { name } = req.body;
    
    if (!name || !name.trim()) {
        return res.status(400).json({ message: 'Name is required' });
    }
    
    const userIndex = users.findIndex(user => user.id === id);
    
    if (userIndex === -1) {
        return res.status(404).json({ message: 'User not found' });
    }
    
    const updatedUser = { id, name };
    users[userIndex] = updatedUser;
    
    res.json(updatedUser);
});

// DELETE user
router.delete('/:id', (req, res) => {
    const id = parseInt(req.params.id);
    const initialLength = users.length;
    
    users = users.filter(user => user.id !== id);
    
    if (users.length === initialLength) {
        return res.status(404).json({ message: 'User not found' });
    }
    
    res.json({ message: 'User deleted successfully' });
});

module.exports = router;
