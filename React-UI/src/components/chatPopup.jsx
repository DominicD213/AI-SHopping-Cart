import React, { useState, useEffect } from "react";
import styled from "styled-components";
import axios from "axios";

const ChatContainer = styled.div`
    margin-top:3rem;
    margin-left: 10rem;
    width: 300px;
    max-height: 400px;
    background-color: white;
    border: 1px solid #ddd;ß
    border-radius: 10px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    display: ${(props) => (props.isOpen ? "flex" : "none")};
    flex-direction: column;
    z-index: 1000;
`;

const ChatHeader = styled.div`
    background-color: black;
    color: white;
    padding: 10px;
    border-top-left-radius: 10px;
    border-top-right-radius: 10px;
    display: flex;
    justify-content: space-between;
    align-items: center;
`;

const CloseButton = styled.span`
    cursor: pointer;
`;

const ChatContent = styled.div`
    flex: 1;
    padding: 10px;
    overflow-y: auto;
    height: 250px;
`;

const Message = styled.div`
    padding: 8px 10px;
    margin: 5px 0;
    border-radius: 8px;
    max-width: 80%;
    align-self: ${(props) => (props.isUser ? "flex-end" : "flex-start")};
    background-color: ${(props) => (props.isUser ? "#007bff" : "#f1f1f1")};
    color: ${(props) => (props.isUser ? "white" : "black")};
`;

const Suggestion = styled.div`
    padding: 8px 10px;
    margin: 5px 0;
    border-radius: 8px;
    background-color: black;
    color: black;
`;

const ChatInputContainer = styled.div`
    display: flex;
    padding: 10px;
    border-top: 1px solid #ddd;
`;

const ChatInput = styled.input`
    flex: 1;
    padding: 8px;
    border: 1px solid #ddd;
    border-radius: 5px;
    margin-right: 5px;
`;

const SendButton = styled.button`
    background-color: black;
    color: white;
    border: none;
    padding: 8px 10px;
    border-radius: 5px;
    cursor: pointer;
`;

const ChatPopup = ({ isOpen, toggleChat, viewedItems }) => {
    const [messages, setMessages] = useState([]);
    const [inputValue, setInputValue] = useState("");
    const [suggestions, setSuggestions] = useState([]);

    // Fetch suggestions based on viewed items when the popup opens
    useEffect(() => {
        const fetchSuggestions = async () => {
            try {
                const response = await axios.get("/api/get_suggestions", {
                    params: { viewed_items: viewedItems }
                });
                setSuggestions(response.data); // Assuming response.data is an array of suggestions
            } catch (error) {
                console.error("Failed to fetch suggestions:", error);
            }
        };

        if (isOpen) {
            fetchSuggestions();
        }
    }, [isOpen, viewedItems]);

    const handleInputChange = (e) => {
        setInputValue(e.target.value);
    };

    const handleSendMessage = async () => {
        if (!inputValue.trim()) return;

        // Add user message to chat
        setMessages((prevMessages) => [
            ...prevMessages,
            { text: inputValue, isUser: true },
        ]);

        // Simulate API call to get AI response (for now we just clear input)
        const aiMessage = "Thank you for your message."; // Replace with actual AI call if needed
        setMessages((prevMessages) => [
            ...prevMessages,
            { text: aiMessage, isUser: false },
        ]);

        // Clear input field
        setInputValue("");
    };

    return (
        <ChatContainer isOpen={isOpen}>
            <ChatHeader>
                <h3>Chat with AI</h3>
                <CloseButton onClick={toggleChat}>&times;</CloseButton>
            </ChatHeader>
            <ChatContent>
                {messages.map((message, index) => (
                    <Message key={index} isUser={message.isUser}>
                        {message.text}
                    </Message>
                ))}
                {/* Display suggestions */}
                {suggestions.map((suggestion) => (
                    <Suggestion key={suggestion.id}>
                        {suggestion.name} - ${suggestion.price}
                    </Suggestion>
                ))}
            </ChatContent>
            <ChatInputContainer>
                <ChatInput
                    type="text"
                    value={inputValue}
                    onChange={handleInputChange}
                    onKeyDown={(e) => {
                        if (e.key === "Enter") handleSendMessage();
                    }}
                    placeholder="Type your message..."
                />
                <SendButton onClick={handleSendMessage}>Send</SendButton>
            </ChatInputContainer>
        </ChatContainer>
    );
};

export default ChatPopup;
