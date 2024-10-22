module.exports = {
  content: ["./src/**/*.{html,js}"],
    theme: {
      extend: {
        colors: {
          bg: 'var(--bg)',
          border: 'var(--border)',
          green: {
            5: 'var(--green5)',
            6: 'var(--green6)',
            // Add more as needed
          },
          gs: {
            10: 'var(--gs10)',
            90: 'var(--gs90)',
            // Add more as needed
          },
        },
      },
    },
  }
  