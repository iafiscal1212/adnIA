import React, { useState, useRef } from 'react';
import './InputArea.css';

const InputArea = ({ onSendMessage, isLoading }) => {
    const [inputValue, setInputValue] = useState('');
    const [selectedFile, setSelectedFile] = useState(null);
    const fileInputRef = useRef(null);

    const handleSend = () => {
        if (inputValue.trim() || selectedFile) {
            onSendMessage(inputValue, selectedFile);
            setInputValue('');
            setSelectedFile(null);
            if(fileInputRef.current) {
                fileInputRef.current.value = '';
            }
        }
    };

    const handleFileChange = (e) => {
        if (e.target.files.length > 0) {
            setSelectedFile(e.target.files[0]);
        }
    };

    const handleUploadClick = () => {
        fileInputRef.current.click();
    };

    return (
        <div className="input-area">
            <button onClick={handleUploadClick} className="upload-button" disabled={isLoading}>📎</button>
            <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileChange}
                style={{ display: 'none' }}
                accept=".pdf,.png"
            />
            <textarea
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
                placeholder="Escribe tu consulta o sube un archivo..."
                rows="1"
                disabled={isLoading}
            />
            <button onClick={handleSend} disabled={isLoading}>
                {isLoading ? '...' : '➤'}
            </button>
            {selectedFile && <div className="file-preview">Archivo: {selectedFile.name}</div>}
        </div>
    );
};

export default InputArea;
