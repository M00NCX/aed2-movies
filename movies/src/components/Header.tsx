import React from 'react';

const Header: React.FC = () => {
  return (
    <header className="py-6 px-8 flex items-center space-x-4 justify-center">
      <img
        src="/logo.svg"
        alt="logo"
        width={100}
        height={100}
        className="w-[100px] h-[100px]"
      />
      <h1 className="text-2xl font-bold text-purple-700">MovieSearch</h1>
    </header>
  );
};

export default Header;
