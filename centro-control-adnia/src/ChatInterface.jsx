import React, { useState, useEffect, useCallback } from 'react';
import Sidebar from './components/chat/Sidebar';
import ChatWindow from './components/chat/ChatWindow';
import InputArea from './components/chat/InputArea';
import './ChatInterface.css';

const ChatInterface = ({ initialJurisdiction, onBack }) => {
    const [conversations, setConversations] = useState([]);
    const [currentConversationId, setCurrentConversationId] = useState(null);
    const [messages, setMessages] = useState([]);
    const [isLoading, setIsLoading] = useState(false);

    // Cargar el historial de conversaciones del usuario
    const fetchConversations = useCallback(async () => {
        try {
            const response = await fetch('/api/chat/history', {
                headers: { 'Content-Type': 'application/json' },
            });
            if (response.ok) {
                const data = await response.json();
                setConversations(data.conversations || []);
            }
        } catch (error) {
            console.error("Error fetching conversations:", error);
        }
    }, []);

    useEffect(() => {
        fetchConversations();
    }, [fetchConversations]);

    const handleSendMessage = async (message, file = null) => {
        if (!message.trim()) return;
        setIsLoading(true);

        const userMessage = { role: 'user', content: message };
        setMessages(prev => [...prev, userMessage]);

        // TODO: Implementar lógica de subida de archivos
        let filePath = null;
        if (file) {
            // ...lógica para subir archivo y obtener la ruta...
            console.log("Archivo a subir:", file.name);
        }

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: message,
                    conversation_id: currentConversationId,
                    file_path: filePath,
                }),
            });

            if (response.ok) {
                const data = await response.json();
                const aiMessage = { role: 'assistant', content: data.response };
                setMessages(prev => [...prev, aiMessage]);
                if (!currentConversationId) {
                    setCurrentConversationId(data.conversation_id);
                    fetchConversations(); // Actualizar la lista de conversaciones
                }
            } else {
                const errorData = await response.json();
                const errorMessage = { role: 'assistant', content: `Error: ${errorData.error}` };
                setMessages(prev => [...prev, errorMessage]);
            }
        } catch (error) {
            const errorMessage = { role: 'assistant', content: `Error de red: ${error.message}` };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    const startNewChat = () => {
        setCurrentConversationId(null);
        setMessages([]);
    };

    return (
        <div className="chat-interface-container">
            <Sidebar
                conversations={conversations}
                onNewChat={startNewChat}
                onSelectConversation={setCurrentConversationId}
                activeConversationId={currentConversationId}
                onBack={onBack}
            />
            <div className="chat-main-area">
                <ChatWindow messages={messages} isLoading={isLoading} />
                <InputArea onSendMessage={handleSendMessage} isLoading={isLoading} />
            </div>
        </div>
    );
};

export default ChatInterface;
