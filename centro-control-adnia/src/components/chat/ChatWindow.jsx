import React, { useRef, useEffect } from 'react';
import './ChatWindow.css';

const ChatWindow = ({ messages, isLoading }) => {
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(scrollToBottom, [messages]);

    return (
        <div className="chat-window">
            {messages.map((msg, index) => (
                <div key={index} className={`message ${msg.role}`}>
                    <div className="message-content">
                        {msg.content}
                    </div>
                </div>
            ))}
            {isLoading && (
                <div className="message assistant">
                    <div className="message-content loading-dots">
                        <span>.</span><span>.</span><span>.</span>
                    </div>
                </div>
            )}
            <div ref={messagesEndRef} />
        </div>
    );
};

export default ChatWindow;
