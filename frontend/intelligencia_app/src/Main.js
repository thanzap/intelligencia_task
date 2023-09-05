import React, { useState } from "react";
import LoginForm from "./LoginForm";
import SignupForm from "./SignupForm";
import "./MainPage.css";

const MainPage = () => {
  const [showLogin, setShowLogin] = useState(true);

  return (
    <div className="main-container">
      <div className="centered-content">
        {showLogin ? <LoginForm /> : <SignupForm />}

        {/* Switching between forms */}
        {showLogin ? (
          <p>
            Don't have an account?{" "}
            <a className="link" onClick={() => setShowLogin(false)}>
              Sign Up
            </a>
          </p>
        ) : (
          <p>
            Already have an account?{" "}
            <a className="link" onClick={() => setShowLogin(true)}>
              Login
            </a>
          </p>
        )}
      </div>
    </div>
  );
};

export default MainPage;
