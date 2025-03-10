import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';

const SidebarMenu = () => {
  const [openMenus, setOpenMenus] = useState({});
  const [isPinned, setPinned] = useState(false);
  const [isSidebarHovered, setSidebarHovered] = useState(false);
  const [isToggled, setToggled] = useState(false);
  const location = useLocation();

  // Handle window resize
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth <= 768) {
        setPinned(false);
      }
      if (window.innerWidth >= 768) {
        setToggled(false);
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Handle sidebar menu click
  const handleMenuClick = (event, menuKey) => {
    // If the clicked item has a submenu, prevent default navigation
    const hasSubmenu = event.currentTarget.nextElementSibling?.classList.contains('treeview-menu');
    
    if (hasSubmenu) {
      event.preventDefault();
      
      setOpenMenus(prevState => {
        const newState = { ...prevState };
        
        // If clicked menu is already open, close it
        if (newState[menuKey]) {
          delete newState[menuKey];
        } else {
          // Close all other menus at the same level and open this one
          Object.keys(newState).forEach(key => {
            if (key.split('-').length === menuKey.split('-').length) {
              delete newState[key];
            }
          });
          
          // Open this menu
          newState[menuKey] = true;
        }
        
        return newState;
      });
    }
  };

  // Toggle sidebar
  const toggleSidebar = () => {
    setToggled(!isToggled);
  };

  // Pin sidebar
  const togglePin = () => {
    setPinned(!isPinned);
  };

  // Handle sidebar hover
  const handleSidebarMouseEnter = () => {
    if (isPinned) {
      setSidebarHovered(true);
    }
  };

  const handleSidebarMouseLeave = () => {
    if (isPinned) {
      setSidebarHovered(false);
    }
  };

  // Recursive function to render menu items and their children
  const renderMenuItem = (item, index, parentKey = '') => {
    const menuKey = parentKey ? `${parentKey}-${index}` : `menu-${index}`;
    const isActive = location.pathname === item.path;
    const hasChildren = item.children && item.children.length > 0;
    const isOpen = openMenus[menuKey];
    
    return (
      <li 
        key={menuKey} 
        className={`${hasChildren ? 'treeview' : ''} ${isActive ? 'active' : ''} ${isOpen ? 'menu-open' : ''}`}
      >
        {item.path ? (
          <Link 
            to={item.path} 
            className={isActive ? 'active' : ''}
            onClick={(e) => hasChildren && handleMenuClick(e, menuKey)}
          >
            {item.icon && <i className={item.icon} />}
            <span className="menu-text">{item.label}</span>
            {item.badge && (
              <span className={`badge ${item.badgeClass || 'bg-primary'} ms-auto`}>
                {item.badge}
              </span>
            )}
            {hasChildren && <i className="ri-arrow-right-s-line" />}
          </Link>
        ) : (
          <a 
            href="#!" 
            className={item.disabled ? 'disabled' : ''}
            onClick={(e) => hasChildren && handleMenuClick(e, menuKey)}
          >
            {item.icon && <i className={item.icon} />}
            <span className="menu-text">{item.label}</span>
            {item.badge && (
              <span className={`badge ${item.badgeClass || 'bg-primary'} ms-auto`}>
                {item.badge}
              </span>
            )}
            {hasChildren && <i className="ri-arrow-right-s-line" />}
          </a>
        )}
        
        {hasChildren && (
          <ul className={`treeview-menu ${isOpen ? 'menu-open' : ''}`} style={{
            display: isOpen ? 'block' : 'none',
            transition: 'height 300ms ease',
          }}>
            {item.children.map((child, childIndex) => 
              renderMenuItem(child, childIndex, menuKey)
            )}
          </ul>
        )}
      </li>
    );
  };

  return (
    <>
      {/* Overlay for mobile */}
      {isToggled && (
        <div id="overlay" onClick={toggleSidebar} className="overlay"></div>
      )}
      
      {/* Sidebar toggler */}
      <button className="toggle-sidebar" onClick={toggleSidebar}>
        <i className="ri-menu-line"></i>
      </button>
      
      {/* Pin sidebar button */}
      <button className="pin-sidebar" onClick={togglePin}>
        <i className={`ri-pushpin-${isPinned ? 'fill' : 'line'}`}></i>
      </button>
      
      {/* Page wrapper */}
      <div className={`page-wrapper ${isToggled ? 'toggled' : ''} ${isPinned ? 'pinned' : ''} ${isSidebarHovered ? 'sidebar-hovered' : ''}`}>
        
        {/* Sidebar */}
        <nav 
          id="sidebar" 
          className="sidebar-wrapper"
          onMouseEnter={handleSidebarMouseEnter}
          onMouseLeave={handleSidebarMouseLeave}
        >
          {/* Sidebar content */}
          {/* ... rest of your sidebar content ... */}
          
          {/* Sidebar menu */}
          <div className="sidebarMenuScroll">
            <ul className="sidebar-menu">
              {menuItems.map((item, index) => renderMenuItem(item, index))}
            </ul>
          </div>
        </nav>
        
        {/* Main content */}
        <div className="main-content">
          {/* Your main content goes here */}
        </div>
      </div>
    </>
  );
};

// Example menu data structure
const menuItems = [
  {
    label: 'Hospital Dashboard',
    icon: 'ri-home-6-line',
    path: '/hospital-dashboard'
  },
  {
    label: 'Dashboard',
    icon: 'ri-home-smile-2-line',
    path: '/'
  },
  {
    label: 'Liste des médécins',
    icon: 'ri-home-smile-2-line',
    path: '/medecinliste'
  },
  {
    label: 'Dentist Dashboard',
    icon: 'ri-home-5-line',
    path: '/dentist-dashboard'
  },
  {
    label: 'Doctors',
    icon: 'ri-stethoscope-line',
    children: [
      { label: 'Doctors Dashboard', path: '/doctor-dashboard' },
      { label: 'Doctors List', path: '/doctors-list' },
    ]
  },
  // Add more menu items as needed
];

export default SidebarMenu;