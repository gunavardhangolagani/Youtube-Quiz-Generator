// Header.jsx
import React from "react";
import { Youtube } from "lucide-react";
import { NavLink } from "react-router-dom";


const Header = ({ onNavigate, currentRoute }) => {
  return (
    <header className="bg-white shadow-sm border-b border-slate-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-3">
            <div className="flex items-center justify-center w-10 h-10 bg-emerald-600 rounded-lg">
              <Youtube className="w-6 h-6 text-white" />
            </div>
            <h1 className="text-xl font-bold text-slate-900 font-inter">
              YouTube Quiz Generator
            </h1>
          </div>
          <nav className="hidden md:flex items-center space-x-6">
            <button
              onClick={() => onNavigate("/")}
              className={`font-medium transition-colors ${
                currentRoute === "/"
                  ? "text-emerald-600"
                  : "text-slate-600 hover:text-emerald-600"
              }`}
            >
              Home
            </button>
            <NavLink
              to="/about"
              className={({ isActive }) =>
                `font-medium transition-colors ${
                  isActive ? "text-emerald-600" : "text-slate-600 hover:text-emerald-600"
                }`
              }
            >
              About
            </NavLink>
          </nav>
        </div>
      </div>
    </header>
  );
};

export default Header;
