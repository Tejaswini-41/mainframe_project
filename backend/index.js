const express = require('express');
const cors = require('cors');
const usersRoute = require('./routes/user');

const app = express();
app.use(cors());
app.use(express.json());

app.use('/api/users', usersRoute);

const PORT = 5000;
app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
});
