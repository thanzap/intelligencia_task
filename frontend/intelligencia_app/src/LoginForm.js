import React, { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import "./LoginForm.css";
import logo from "./104766.png";

const LoginForm = (props) => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post("http://localhost:8000/api/v1/login/", {
        username,
        password,
      });

      // Store the token to localStorage for demonstration purposes
      // Please be aware of security implications of storing tokens in localStorage
      localStorage.setItem("access_token", response.data.access_token);
      localStorage.setItem("refresh_token", response.data.refresh_token);
      navigate("/dashboard");
      // Redirect or perform any other logic post-login
    } catch (error) {
      setErrorMessage("Invalid credentials. Please try again.");
      console.error("An error occurred during login:", error);
    }
  };

  return (
    <div className="container">
      <h2>Login</h2>
      <img src={logo} alt="intelligencia_logo"></img>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <button type="submit">Login</button>
      </form>
      {errorMessage && <p>{errorMessage}</p>}
    </div>
  );
};

export default LoginForm;
