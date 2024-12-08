import React, { useState, useEffect } from 'react';
import axios from 'axios';

const App = () => {
  const [tables, setTables] = useState([]);
  const [rows, setRows] = useState([]);
  const [columns, setColumns] = useState([]);
  const [newRow, setNewRow] = useState({});
  const [rowIdToUpdate, setRowIdToUpdate] = useState(null);
  const [updatedData, setUpdatedData] = useState({});
  const [tableName, setTableName] = useState('');

  // Fetch tables from the backend
  useEffect(() => {
    axios.get('http://localhost:5000/api/tables')
      .then(response => {
        setTables(response.data);
      })
      .catch(error => {
        console.error('Error fetching tables:', error);
      });
  }, []);

  // Fetch columns for a particular table
  const getColumns = (tableName) => {
    if (!tableName) return;
    axios.get(`http://localhost:5000/api/columns/${tableName}`)
      .then(response => {
        setColumns(response.data);
      })
      .catch(error => {
        console.error(`Error fetching columns for table ${tableName}:`, error);
      });
  };

  // Fetch rows for a particular table
  const getRows = (tableName) => {
    if (!tableName) return;
    axios.get(`http://localhost:5000/api/rows/${tableName}`)
      .then(response => {
        setRows(response.data);
      })
      .catch(error => {
        console.error(`Error fetching rows from table ${tableName}:`, error);
      });
      console.log('Rows', rows);
  };

  // Insert a new row
  const insertRow = () => {
    axios.post(`http://localhost:5000/api/insert_row/${tableName}`, newRow)
      .then(response => {
        console.log('Row inserted successfully:', response.data);
        getRows(tableName);  // Refresh the rows after insert
      })
      .catch(error => {
        console.error('Error inserting row:', error);
      });
  };

  // Update an existing row
  const updateRow = (rowId) => {
    axios.put(`http://localhost:5000/api/update_row/${tableName}/${rowId}`, updatedData)
      .then(response => {
        console.log('Row updated successfully:', response.data);
        getRows(tableName);  // Refresh the rows after update
      })
      .catch(error => {
        console.error('Error updating row:', error);
      });
  };

  // Delete a row
  const deleteRow = (rowId) => {
    axios.delete(`http://localhost:5000/api/delete_row/${tableName}/${rowId}`)
      .then(response => {
        console.log('Row deleted successfully:', response.data);
        getRows(tableName);  // Refresh the rows after delete
      })
      .catch(error => {
        console.error('Error deleting row:', error);
      });
  };

  return (
    <div>
      <h1>Database Management</h1>
      <div>
        <h2>Tables</h2>
        <ul>
          {tables.map((table, index) => (
            <li key={index}>
              <button onClick={() => { 
                setTableName(table[0]); 
                getRows(table[0]);
                getColumns(table[0]); 
              }}>
                {table[0]}
              </button>
            </li>
          ))}
        </ul>
      </div>

      {tableName && (
        <div>
          <h2>Rows in {tableName}</h2>
          <ul>
            {rows.map((row, index) => (
              <li key={index}>
                {row.join(' | ')}
                <button onClick={() => deleteRow(row[0])}>Delete</button>
                <button onClick={() => setRowIdToUpdate(row[0])}>Update</button>
              </li>
            ))}
          </ul>

          <h2>Insert Row</h2>
          {columns.map((column, index) => (
            <input
              key={index}
              type="text"
              placeholder={column}
              onChange={e => setNewRow({ ...newRow, [column]: e.target.value })}
            />
          ))}
          <button onClick={insertRow}>Insert</button>

          <h2>Update Row</h2>
          <input
            type="text"
            placeholder="Row ID"
            onChange={e => setRowIdToUpdate(e.target.value)}
          />
          {columns.map((column, index) => (
            <input
              key={index}
              type="text"
              placeholder={`Update ${column}`}
              onChange={e => setUpdatedData({ ...updatedData, [column]: e.target.value })}
            />
          ))}
          <button onClick={() => updateRow(rowIdToUpdate)}>Update Row</button>
        </div>
      )}
    </div>
  );
};

export default App;
