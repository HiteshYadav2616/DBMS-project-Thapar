import './Toast.css';

export default function Toast({ message, type = 'info', onClose }) {
  return (
    <div className={`toast toast-${type}`} onAnimationEnd={(e) => { if (e.animationName === 'toastOut') onClose(); }}>
      {message}
    </div>
  );
}
