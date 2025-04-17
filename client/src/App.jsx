import { useEffect, useState } from 'react';
import './App.css';

function App() {
  const [users, setUsers] = useState([]);
  const [newUser, setNewUser] = useState({ name: '' });
  const [editingUser, setEditingUser] = useState(null);
  const [loading, setLoading] = useState(false);

  // Fetch all users
  const fetchUsers = async () => {
    setLoading(true);
    try {
      const res = await fetch('http://localhost:5000/api/users');
      const data = await res.json();
      setUsers(data);
    } catch (error) {
      console.error('Error fetching users:', error);
    } finally {
      setLoading(false);
    }
  };

  // Load users on component mount
  useEffect(() => {
    fetchUsers();
  }, []);

  // Add a new user
  const handleAddUser = async (e) => {
    e.preventDefault();
    if (!newUser.name.trim()) return;

    try {
      const res = await fetch('http://localhost:5000/api/users', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newUser)
      });
      
      if (res.ok) {
        const addedUser = await res.json();
        setUsers([...users, addedUser]);
        setNewUser({ name: '' });
      }
    } catch (error) {
      console.error('Error adding user:', error);
    }
  };

  // Delete a user
  const handleDeleteUser = async (id) => {
    try {
      const res = await fetch(`http://localhost:5000/api/users/${id}`, {
        method: 'DELETE'
      });
      
      if (res.ok) {
        setUsers(users.filter(user => user.id !== id));
      }
    } catch (error) {
      console.error('Error deleting user:', error);
    }
  };

  // Start editing a user
  const startEditing = (user) => {
    setEditingUser({ ...user });
  };

  // Cancel editing
  const cancelEditing = () => {
    setEditingUser(null);
  };

  // Update a user
  const handleUpdateUser = async (e) => {
    e.preventDefault();
    if (!editingUser || !editingUser.name.trim()) return;

    try {
      const res = await fetch(`http://localhost:5000/api/users/${editingUser.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(editingUser)
      });
      
      if (res.ok) {
        const updatedUser = await res.json();
        setUsers(users.map(user => 
          user.id === updatedUser.id ? updatedUser : user
        ));
        setEditingUser(null);
      }
    } catch (error) {
      console.error('Error updating user:', error);
    }
  };

  return (
    <div className="app-container">
      <h1>User Management System</h1>
      
      {/* Add User Form */}
      <div className="form-container">
        <h2>Add New User</h2>
        <form onSubmit={handleAddUser}>
          <input
            type="text"
            placeholder="Enter user name"
            value={newUser.name}
            onChange={(e) => setNewUser({ name: e.target.value })}
          />
          <button type="submit">Add User</button>
        </form>
      </div>
      
      {/* Edit User Form */}
      {editingUser && (
        <div className="form-container">
          <h2>Edit User</h2>
          <form onSubmit={handleUpdateUser}>
            <input
              type="text"
              value={editingUser.name}
              onChange={(e) => setEditingUser({ ...editingUser, name: e.target.value })}
            />
            <div className="button-group">
              <button type="submit">Update</button>
              <button type="button" onClick={cancelEditing}>Cancel</button>
            </div>
          </form>
        </div>
      )}
      
      {/* User List */}
      <div className="user-list">
        <h2>Users</h2>
        {loading ? (
          <p>Loading users...</p>
        ) : users.length === 0 ? (
          <p>No users found</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.map(user => (
                <tr key={user.id}>
                  <td>{user.id}</td>
                  <td>{user.name}</td>
                  <td>
                    <button onClick={() => startEditing(user)}>Edit</button>
                    <button onClick={() => handleDeleteUser(user.id)}>Delete</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

export default App;
