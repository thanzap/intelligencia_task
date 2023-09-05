import React, { useState, useEffect } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import "./Dashboard.css";
import logo from "./104766.png";

const Dashboard = () => {
  const [data, setData] = useState({ results: [] });
  const navigate = useNavigate();
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 50; // assuming each page shows 50 items
  const totalPages = Math.ceil(data.count / itemsPerPage);
  const [next_url, setNextUrl] = useState(null);
  const [previous_url, setPreviousUrl] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");
  const first_url = "http://localhost:8000/api/v1/efoterms/?page=1";
  const last_url = `http://localhost:8000/api/v1/efoterms/?page=${totalPages}`;
  const [term_data, setTerm_data] = useState(null);
  const [errorMessage, setErrorMessage] = useState("");
  const [flag, setFlag] = useState(true);

  const handleSearchChange = (event) => {
    setSearchTerm(event.target.value);
  };

  const handleSearchSubmit = (event) => {
    event.preventDefault();
    termData();
  };

  const handleLogout = () => {
    // Clear the token from local storage
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");

    // Navigate the user back to the login page (or wherever you'd like)
    navigate("/");
  };

  const termData = async () => {
    try {
      const response = await axios.get(
        `http://localhost:8000/api/v1/efoterm/`,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("access_token")}`,
          },
          params: {
            efo_term_id: searchTerm.trim(),
          },
        }
      );
      setTerm_data(response.data);
      setFlag(false);
      setErrorMessage("");
    } catch (error) {
      if (error.response) {
        if (error.response.status === 401) {
          // Unauthorized, try refreshing the token
          try {
            const refreshResponse = await axios.post(
              "http://localhost:8000/api/v1/token/refresh/",
              {
                refresh: localStorage.getItem("refresh_token"),
              }
            );
            localStorage.setItem("access_token", refreshResponse.data.access);
            termData();
            setErrorMessage("");
          } catch (refreshError) {
            // The refresh token is probably also expired, so re-authenticate
            handleLogout();
          }
        } else if (error.response.status === 404) {
          setErrorMessage("EFO term not found. Please try again.");
          setFlag(true);
        } else if (error.response.status === 400) {
          setErrorMessage("No Term ID provided");
          setFlag(true);
        }
      }
    }
  };

  const fetchData = async (
    url = "http://localhost:8000/api/v1/efoterms/?page=1"
  ) => {
    try {
      const response = await axios.get(url, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
      });
      setSearchTerm("");
      setErrorMessage("");
      setData(response.data);
      setNextUrl(response.data.next);
      setPreviousUrl(response.data.previous);
      setFlag(true);
    } catch (error) {
      if (error.response && error.response.status === 401) {
        // Unauthorized, try refreshing the token
        try {
          const refreshResponse = await axios.post(
            "http://localhost:8000/api/v1/token/refresh/",
            {
              refresh: localStorage.getItem("refresh_token"),
            }
          );
          localStorage.setItem("access_token", refreshResponse.data.access);
          fetchData(url);
          setErrorMessage("");
        } catch (refreshError) {
          // The refresh token is probably also expired, so re-authenticate
          handleLogout();
        }
      }
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleNextClick = () => {
    if (next_url) {
      fetchData(next_url);
      setCurrentPage(currentPage + 1);
      handleScrollToTop();
    }
  };

  const handlePreviousClick = () => {
    if (previous_url) {
      fetchData(previous_url);
      setCurrentPage(currentPage - 1);
      handleScrollToTop();
    }
  };

  const handleStartClick = () => {
    fetchData(first_url);
    setCurrentPage(1);
    handleScrollToTop();
  };

  const handleEndClick = () => {
    fetchData(last_url);
    setCurrentPage(totalPages);
    handleScrollToTop();
  };

  const handleClearClick = () => {
    fetchData(first_url);
    setCurrentPage(1);
  };

  const handleScrollToTop = () => {
    window.scrollTo({
      top: 0,
      left: 0,
      behavior: "smooth",
    });
  };

  return (
    <div className="dashboard">
      <div className="header">
        <img src={logo} alt="intelligencia_logo"></img>
        <button className="logout" onClick={handleLogout}>
          Logout
        </button>
        <h2>EFO Terms</h2>
        <form onSubmit={handleSearchSubmit}>
          <input
            type="search"
            value={searchTerm}
            onChange={handleSearchChange}
            placeholder="Search..."
          />
          <button className="search" type="submit">
            Search
          </button>
          <button onClick={handleClearClick} className="search" type="text">
            Clear
          </button>
        </form>
        {errorMessage && <p className="search_errors">{errorMessage}</p>}
      </div>
      {flag ? (
        <div className="pagination">
          <h3>
            Page: {currentPage}/{totalPages}{" "}
          </h3>
          <div>
            {currentPage > 1 && (
              <button onClick={handleStartClick}>First</button>
            )}
            {currentPage < totalPages && (
              <button onClick={handleNextClick}>Next</button>
            )}
            {currentPage > 1 && (
              <button onClick={handlePreviousClick}>Previous</button>
            )}
            {currentPage < totalPages && (
              <button onClick={handleEndClick}>Last</button>
            )}
          </div>
        </div>
      ) : null}
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Synonyms</th>
          </tr>
        </thead>
        <tbody>
          {flag ? (
            data.results.map((item) => (
              <tr key={item.efo_term_id}>
                <td>{item.efo_term_id}</td>
                <td>{item.term_name}</td>
                <td>{item.synonyms.join(", ")}</td>
              </tr>
            ))
          ) : (
            <tr key={term_data.efo_term_id}>
              <td>{term_data.efo_term_id}</td>
              <td>{term_data.term_name}</td>
              <td>{term_data.synonyms.join(", ")}</td>
            </tr>
          )}
        </tbody>
      </table>
      {flag ? (
        <div className="pagination">
          <h3>
            Page: {currentPage}/{totalPages}{" "}
          </h3>
          <div>
            {currentPage > 1 && (
              <button onClick={handleStartClick}>First</button>
            )}
            {currentPage < totalPages && (
              <button onClick={handleNextClick}>Next</button>
            )}
            {currentPage > 1 && (
              <button onClick={handlePreviousClick}>Previous</button>
            )}
            {currentPage < totalPages && (
              <button onClick={handleEndClick}>Last</button>
            )}
          </div>
        </div>
      ) : null}
    </div>
  );
};

export default Dashboard;
