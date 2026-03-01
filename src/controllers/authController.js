import authService from '../services/authService.js';

class AuthController {
  /**
   * Register a new user
   * POST /api/auth/register
   */
  async register(req, res) {
    try {
      const { email, password, name } = req.body;

      // Validate input
      if (!email || !password || !name) {
        return res.status(400).json({
          error: 'Validation error',
          message: 'Email, password, and name are required'
        });
      }

      // Validate email format
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(email)) {
        return res.status(400).json({
          error: 'Validation error',
          message: 'Invalid email format'
        });
      }

      // Validate password length
      if (password.length < 6) {
        return res.status(400).json({
          error: 'Validation error',
          message: 'Password must be at least 6 characters long'
        });
      }

      // Register user
      const user = await authService.register(email, password, name);

      res.status(201).json({
        message: 'User registered successfully',
        user
      });
    } catch (error) {
      if (error.statusCode) {
        return res.status(error.statusCode).json({
          error: error.message
        });
      }

      console.error('Registration error:', error);
      res.status(500).json({
        error: 'Internal server error',
        message: 'Failed to register user'
      });
    }
  }

  /**
   * Login user
   * POST /api/auth/login
   */
  async login(req, res) {
    try {
      const { email, password } = req.body;

      // Validate input
      if (!email || !password) {
        return res.status(400).json({
          error: 'Validation error',
          message: 'Email and password are required'
        });
      }

      // Authenticate user
      const { user, token } = await authService.login(email, password);

      res.status(200).json({
        message: 'Login successful',
        user,
        token
      });
    } catch (error) {
      if (error.statusCode) {
        return res.status(error.statusCode).json({
          error: error.message
        });
      }

      console.error('Login error:', error);
      res.status(500).json({
        error: 'Internal server error',
        message: 'Failed to login'
      });
    }
  }

  /**
   * Get current user profile
   * GET /api/auth/me
   */
  async getCurrentUser(req, res) {
    try {
      // User is already attached by auth middleware
      res.status(200).json({
        user: req.user
      });
    } catch (error) {
      console.error('Get current user error:', error);
      res.status(500).json({
        error: 'Internal server error',
        message: 'Failed to get user profile'
      });
    }
  }

  /**
   * Logout user (client-side token removal)
   * POST /api/auth/logout
   */
  async logout(req, res) {
    // JWT tokens are stateless, so logout is handled client-side
    // This endpoint exists for consistency and future session management
    res.status(200).json({
      message: 'Logout successful'
    });
  }
}

export default new AuthController();
