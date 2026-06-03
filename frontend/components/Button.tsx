type ButtonProps = {
  label: string;
  onClick?: () => void;
};

export function Button({ label, onClick }: ButtonProps) {
  return (
    <button className="primary-button" type="button" onClick={onClick}>
      {label}
    </button>
  );
}
