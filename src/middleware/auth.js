import authService from '../services/authService.js';

/**
 * Authentication middleware
 * Verifies JWT token and attaches user info to request
 */
export const authenticate = async (req, res, next) => {
  try {
    // Get token from Authorization header
    const authHeader = req.headers.authorization;

    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json({
        error: 'Authentication required',
        message: 'No token provided'
      });
    }

    const token = authHeader.substring(7); // Remove 'Bearer ' prefix

    // Verify token
    const decoded = await authService.verifyToken(token);

    // Get user from database
    const user = await authService.getUserById(decoded.userId);

    // Attach user to request
    req.user = user;
    req.userId = user.id;

    next();
  } catch (error) {
    if (error.statusCode === 401) {
      return res.status(401).json({
        error: 'Authentication failed',
        message: error.message
      });
    }

    return res.status(500).json({
      error: 'Internal server error',
      message: 'Authentication error'
    });
  }
};

/**
 * Optional authentication middleware
 * Attaches user info if token is present, but doesn't require it
 */
export const optionalAuth = async (req, res, next) => {
  try {
    const authHeader = req.headers.authorization;

    if (authHeader && authHeader.startsWith('Bearer ')) {
      const token = authHeader.substring(7);
      const decoded = await authService.verifyToken(token);
      const user = await authService.getUserById(decoded.userId);
      req.user = user;
      req.userId = user.id;
    }

    next();
  } catch (error) {
    // Continue without authentication
    next();
  }
};
