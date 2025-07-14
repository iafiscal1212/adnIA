import React from 'react';
import './Sidebar.css';

const Sidebar = ({ conversations, onNewChat, onSelectConversation, activeConversationId, onBack }) => {
    return (
        <div className="chat-sidebar">
            <div className="sidebar-header">
                <button onClick={onBack} className="back-button">←</button>
                <h2>ADNIA Chat</h2>
                <button onClick={onNewChat} className="new-chat-button">+</button>
            </div>
            <div className="conversations-list">
                <h3>Historial</h3>
                {conversations.length > 0 ? (
                    <ul>
                        {conversations.map(convId => (
                            <li
                                key={convId}
                                className={convId === activeConversationId ? 'active' : ''}
                                onClick={() => onSelectConversation(convId)}
                            >
                                Chat {convId.substring(0, 8)}...
                            </li>
                        ))}
                    </ul>
                ) : (
                    <p>No hay conversaciones.</p>
                )}
            </div>
            {/* Secciones para Pinned y Proyectos se pueden añadir aquí */}
        </div>
    );
};

export default Sidebar;
