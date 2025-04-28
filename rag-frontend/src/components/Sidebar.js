import React from "react";
import { NavLink } from "react-router-dom";

const Sidebar = ({ isOpen, closeSidebar }) => {
  const links = [
    { name: "Dashboard", path: "/dashboard" },
    { name: "Ingest Documents", path: "/ingest" },
    { name: "Ask a Question", path: "/qa" },
  ];

  return (
    <>
      {/* Mobile Overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-40 z-40 md:hidden"
          onClick={closeSidebar}
        />
      )}
      {/* Sidebar */}
      <aside
        className={`fixed z-50 top-16 left-0 h-[calc(100vh-4rem)] w-64 bg-gray-100 shadow-inner transform transition-transform duration-300 ease-in-out
        ${
          isOpen ? "translate-x-0" : "-translate-x-full"
        } md:translate-x-0 md:block`}
      >
        <nav className="p-4 space-y-4">
          {links.map((link) => (
            <NavLink
              key={link.path}
              to={link.path}
              className={({ isActive }) =>
                `block text-sm font-medium ${
                  isActive
                    ? "text-indigo-600"
                    : "text-gray-700 hover:text-indigo-500"
                }`
              }
              onClick={closeSidebar}
            >
              {link.name}
            </NavLink>
          ))}
        </nav>
      </aside>
    </>
  );
};

export default Sidebar;
