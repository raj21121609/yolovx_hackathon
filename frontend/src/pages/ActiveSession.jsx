import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import sessionService from '../services/sessionService';
import { reportService } from '../services/reportService';
import { Camera, CheckCircle, AlertCircle, Users, Clock } from 'lucide-react';

const ActiveSession = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [session, setSession] = useState(null);
  const [attendance, setAttendance] = useState([]);
  const [status, setStatus] = useState({ state: 'IDLE', info: null });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchInit = async () => {
      try {
        const sess = await sessionService.getById(id);
        setSession(sess);
        const att = await sessionService.getAttendance(id);
        setAttendance(att);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchInit();
  }, [id]);

  useEffect(() => {
    if (!session || session.status !== 'ACTIVE') return;

    const interval = setInterval(async () => {
      try {
        const stat = await sessionService.getStatus(id);
        setStatus(stat);
        
        // Refresh attendance if verified recently
        if (stat.info?.verified_events && stat.info.verified_events.length > 0) {
          const att = await sessionService.getAttendance(id);
          setAttendance(att);
        }
      } catch (err) {
        // console.error(err);
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [session, id]);

  const handleEnd = async () => {
    if (window.confirm("Are you sure you want to end this attendance session?")) {
      try {
        const res = await sessionService.end(id);
        setSession(res);
      } catch (err) {
        console.error(err);
      }
    }
  };

  const getStatusMessage = (state) => {
    switch (state) {
      case 'SCANNING': return "Scanning classroom...";
      case 'RECOGNIZING': return "Recognizing faces...";
      case 'UNKNOWN': return "Unknown face(s) detected";
      case 'LOW_QUALITY': return "Lighting/blur issues detected";
      case 'CAMERA_ERROR': return "Camera unavailable";
      default: return "Initializing AI Engine...";
    }
  };

  if (loading) return <div className="p-8">Loading session...</div>;
  if (!session) return <div className="p-8">Session not found</div>;

  const presentCount = attendance.filter(a => a.status === 'PRESENT').length;
  const lateCount = attendance.filter(a => a.status === 'LATE').length;
  // Absent count for MVP is total - present - late (if we had total students). 
  // Let's just show what we have in DB.

  return (
    <div className="p-8 max-w-7xl mx-auto flex flex-col md:flex-row gap-8">
      {/* LEFT: Camera Viewer */}
      <div className="md:w-2/3 flex flex-col gap-6">
        <div className="bg-white rounded-xl shadow-md border border-gray-200/60 overflow-hidden">
          <div className="px-6 py-4 bg-sj-primary border-b border-sj-primary flex justify-between items-center text-white">
            <h2 className="text-lg font-bold flex items-center gap-2 tracking-wide">
              <Camera size={20} /> LIVE CLASSROOM
            </h2>
            <span className={`px-3 py-1 rounded-full text-xs font-bold ${
              session.status !== 'ACTIVE' ? 'bg-white/20 text-white' :
              status.state === 'CAMERA_ERROR' ? 'bg-red-500 text-white' :
              'bg-sj-secondary text-white animate-pulse'
            }`}>
              {session.status !== 'ACTIVE' ? 'OFFLINE' : 
               status.state === 'CAMERA_ERROR' ? '🔴 DISCONNECTED' : '● LIVE'}
            </span>
          </div>
          <div className="bg-gray-900 aspect-video relative flex items-center justify-center">
            {session.status === 'ACTIVE' && session.stream_token ? (
              <img 
                src={`http://localhost:8000/api/sessions/${session.id}/stream/?token=${session.stream_token}`} 
                alt="Live Feed" 
                className="w-full h-full object-contain"
                onError={(e) => {
                  e.target.style.display = 'none';
                  e.target.nextSibling.style.display = 'block';
                }}
              />
            ) : (
              <div className="text-gray-500 flex flex-col items-center">
                <Camera size={48} className="mb-2 opacity-50" />
                <p>Camera is offline</p>
              </div>
            )}
            <div className="hidden text-white absolute inset-0 flex items-center justify-center bg-black bg-opacity-50">Stream Unavailable</div>
          </div>
          <div className="p-6 bg-gray-50">
            <div className="flex items-start gap-4">
              <div className={`p-3 rounded-full ${
                status.state === 'VERIFIED' ? 'bg-green-100 text-green-600' :
                status.state === 'UNKNOWN' ? 'bg-red-100 text-red-600' :
                status.state === 'MULTI_FRAME_VERIFY' ? 'bg-yellow-100 text-yellow-600' :
                'bg-blue-100 text-blue-600'
              }`}>
                {status.state === 'VERIFIED' ? <CheckCircle size={24} /> : <AlertCircle size={24} />}
              </div>
              <div className="flex-1">
                <p className="text-sm font-semibold text-gray-500 uppercase tracking-wider">State: {status.state}</p>
                <p className="text-xl font-medium text-gray-900">{getStatusMessage(status.state)}</p>
                
                {status.info?.unknown_count > 0 && (
                  <div className="mt-2 text-sm text-red-600 font-medium">
                    {status.info.unknown_count} unknown/unregistered face(s) detected
                  </div>
                )}

                {status.info?.verifying && status.info.verifying.length > 0 && (
                  <div className="mt-3 space-y-2">
                    {status.info.verifying.map(v => (
                      <div key={v.student_id} className="text-sm text-yellow-700 bg-yellow-50 p-2 rounded border border-yellow-100 flex justify-between">
                        <span>Verifying <strong>{v.student_name}</strong>...</span>
                        <span>{v.match_count} / {v.required}</span>
                      </div>
                    ))}
                  </div>
                )}
                
                {status.info?.recently_verified && status.info.recently_verified.length > 0 && (
                  <div className="mt-3 space-y-2">
                    {status.info.recently_verified.map(v => (
                      <div key={v.student_id} className="p-3 bg-green-50 border border-green-200 rounded-lg text-green-800 flex justify-between items-center">
                        <span className="font-bold text-lg flex items-center gap-2"><CheckCircle size={18}/> {v.student_name}</span>
                        <span className="text-xs opacity-70">Cooldown: {v.cooldown_remaining.toFixed(1)}s</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* RIGHT: Attendance Summary */}
      <div className="md:w-1/3 flex flex-col gap-6">
        <div className="bg-white rounded-xl shadow-md border border-gray-200/60 p-6">
          <h2 className="text-2xl font-extrabold text-sj-primary mb-1">{session.subject}</h2>
          <p className="text-gray-500 font-medium mb-6">{new Date(session.created_at).toLocaleDateString()}</p>
          
          <div className="grid grid-cols-2 gap-4 mb-6">
            <div className="bg-green-50 p-4 rounded-lg text-center border border-green-100">
              <p className="text-3xl font-bold text-green-700">{presentCount}</p>
              <p className="text-sm font-medium text-green-600">Present</p>
            </div>
            <div className="bg-yellow-50 p-4 rounded-lg text-center border border-yellow-100">
              <p className="text-3xl font-bold text-yellow-700">{lateCount}</p>
              <p className="text-sm font-medium text-yellow-600">Late</p>
            </div>
          </div>
          
          {session.status === 'ACTIVE' ? (
            <button 
              onClick={handleEnd}
              className="w-full py-3 bg-sj-secondary text-white rounded-lg font-bold hover:bg-red-700 shadow-sm transition-all tracking-wider"
            >
              END SESSION
            </button>
          ) : (
            <div className="space-y-3">
              <div className="w-full py-3 bg-gray-100 text-gray-600 rounded-lg font-bold text-center border border-gray-200">
                ATTENDANCE COMPLETED
              </div>
              <button
                onClick={() => reportService.exportSessionCSV(id)}
                className="w-full py-2 border-2 border-sj-primary text-sj-primary rounded-lg font-bold hover:bg-blue-50 transition-colors flex items-center justify-center gap-2"
              >
                Download CSV Report
              </button>
            </div>
          )}
        </div>

        <div className="bg-white rounded-xl shadow-md border border-gray-200/60 flex-1 flex flex-col overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="font-bold text-sj-primary uppercase tracking-wider text-sm">Recent Attendance</h3>
          </div>
          <div className="flex-1 overflow-y-auto p-4 space-y-3">
            {attendance.slice().reverse().map(record => (
              <div key={record.id} className="flex justify-between items-center p-3 hover:bg-gray-50 rounded-lg border border-gray-100 transition-colors">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-full bg-blue-50 text-sj-primary border border-blue-100 flex items-center justify-center font-bold text-sm">
                    {record.student_name.charAt(0)}
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">{record.student_name}</p>
                    <p className="text-xs text-gray-500">{new Date(record.created_at).toLocaleTimeString()}</p>
                  </div>
                </div>
                <span className={`text-xs font-bold px-2 py-1 rounded ${
                  record.status === 'PRESENT' ? 'bg-green-100 text-green-700' : 
                  record.status === 'LATE' ? 'bg-yellow-100 text-yellow-700' : 'bg-red-100 text-red-700'
                }`}>
                  {record.status}
                </span>
              </div>
            ))}
            {attendance.length === 0 && (
              <p className="text-center text-gray-500 py-8">No attendance recorded yet</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ActiveSession;
