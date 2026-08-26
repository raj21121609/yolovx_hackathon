import { useContext } from 'react';
import { Outlet, Link, useNavigate, useLocation } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import { LayoutDashboard, Users, Calendar, LogOut, BarChart2 } from 'lucide-react';

const Sidebar = () => {
  const { logout } = useContext(AuthContext);
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navItems = [
    { path: '/', label: 'Dashboard', icon: <LayoutDashboard size={20} /> },
    { path: '/sessions', label: 'Sessions', icon: <Calendar size={20} /> },
    { path: '/students', label: 'Students', icon: <Users size={20} /> },
    { path: '/reports', label: 'Reports', icon: <BarChart2 size={20} /> },
  ];

  return (
    <div className="w-64 bg-sj-primary text-white min-h-screen flex flex-col shadow-xl z-10 relative">
      <div className="p-6 border-b border-white/10">
        <h1 className="text-2xl font-extrabold tracking-tight">VisionAttend</h1>
        <p className="text-xs text-blue-200 mt-1 uppercase tracking-wider font-semibold">St. John College</p>
      </div>
      <nav className="flex-1 p-4 space-y-1">
        {navItems.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            className={`flex items-center space-x-3 p-3 rounded-lg transition-all duration-200 ${
              location.pathname === item.path 
                ? 'bg-white/10 text-white font-medium shadow-sm border-l-4 border-sj-secondary' 
                : 'text-blue-100 hover:bg-white/5 hover:text-white border-l-4 border-transparent'
            }`}
          >
            {item.icon}
            <span>{item.label}</span>
          </Link>
        ))}
      </nav>
      <div className="p-4 border-t border-white/10">
        <button
          onClick={handleLogout}
          className="flex items-center space-x-3 p-3 w-full rounded-lg text-blue-100 hover:bg-sj-secondary hover:text-white transition-all duration-200"
        >
          <LogOut size={20} />
          <span className="font-medium">Logout</span>
        </button>
      </div>
    </div>
  );
};

const Layout = () => {
  return (
    <div className="flex h-screen bg-sj-accent overflow-hidden font-sans">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Clean top header */}
        <header className="bg-white border-b border-gray-200 h-16 flex items-center px-8 justify-between shrink-0 shadow-sm z-0">
          <div className="font-semibold text-sj-primary text-lg flex items-center gap-2">
            Faculty Dashboard
          </div>
          <div className="text-sm font-medium text-gray-500 bg-gray-100 px-3 py-1 rounded-full border border-gray-200">
            Autonomous Institute | NAAC 'A+' Grade
          </div>
        </header>
        
        {/* Main Content Area */}
        <main className="flex-1 overflow-auto p-6 md:p-8 bg-sj-accent">
          <div className="max-w-7xl mx-auto">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
};

export default Layout;
