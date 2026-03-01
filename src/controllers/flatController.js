import flatService from '../services/flatService.js';

class FlatController {
  /**
   * Create a new flat
   * POST /api/flats
   */
  async createFlat(req, res) {
    try {
      const { name } = req.body;
      const userId = req.userId;

      // Validate input
      if (!name || name.trim().length === 0) {
        return res.status(400).json({
          error: 'Validation error',
          message: 'Flat name is required'
        });
      }

      // Create flat
      const flat = await flatService.createFlat(name.trim(), userId);

      res.status(201).json({
        message: 'Flat created successfully',
        flat
      });
    } catch (error) {
      if (error.statusCode) {
        return res.status(error.statusCode).json({
          error: error.message
        });
      }

      console.error('Create flat error:', error);
      res.status(500).json({
        error: 'Internal server error',
        message: 'Failed to create flat'
      });
    }
  }

  /**
   * Get all flats for the current user
   * GET /api/flats
   */
  async getUserFlats(req, res) {
    try {
      const userId = req.userId;

      const flats = await flatService.getUserFlats(userId);

      res.status(200).json({
        flats
      });
    } catch (error) {
      console.error('Get user flats error:', error);
      res.status(500).json({
        error: 'Internal server error',
        message: 'Failed to retrieve flats'
      });
    }
  }

  /**
   * Get flat by ID
   * GET /api/flats/:flatId
   */
  async getFlatById(req, res) {
    try {
      const { flatId } = req.params;
      const userId = req.userId;

      // Check if user is a member of the flat
      const isMember = await flatService.isUserMemberOfFlat(flatId, userId);
      
      if (!isMember) {
        return res.status(403).json({
          error: 'Access denied',
          message: 'You are not a member of this flat'
        });
      }

      const flat = await flatService.getFlatById(flatId);

      res.status(200).json({
        flat
      });
    } catch (error) {
      if (error.statusCode) {
        return res.status(error.statusCode).json({
          error: error.message
        });
      }

      console.error('Get flat error:', error);
      res.status(500).json({
        error: 'Internal server error',
        message: 'Failed to retrieve flat'
      });
    }
  }

  /**
   * Get all members of a flat
   * GET /api/flats/:flatId/members
   */
  async getFlatMembers(req, res) {
    try {
      const { flatId } = req.params;
      const userId = req.userId;

      // Check if user is a member of the flat
      const isMember = await flatService.isUserMemberOfFlat(flatId, userId);
      
      if (!isMember) {
        return res.status(403).json({
          error: 'Access denied',
          message: 'You are not a member of this flat'
        });
      }

      const members = await flatService.getFlatMembers(flatId);

      res.status(200).json({
        members
      });
    } catch (error) {
      console.error('Get flat members error:', error);
      res.status(500).json({
        error: 'Internal server error',
        message: 'Failed to retrieve flat members'
      });
    }
  }

  /**
   * Add a member to a flat
   * POST /api/flats/:flatId/members
   */
  async addMemberToFlat(req, res) {
    try {
      const { flatId } = req.params;
      const { userId: userIdToAdd } = req.body;
      const currentUserId = req.userId;

      // Validate input
      if (!userIdToAdd) {
        return res.status(400).json({
          error: 'Validation error',
          message: 'User ID is required'
        });
      }

      // Check if current user is a member of the flat
      const isMember = await flatService.isUserMemberOfFlat(flatId, currentUserId);
      
      if (!isMember) {
        return res.status(403).json({
          error: 'Access denied',
          message: 'You are not a member of this flat'
        });
      }

      // Add member
      const member = await flatService.addMemberToFlat(flatId, userIdToAdd);

      res.status(201).json({
        message: 'Member added successfully',
        member
      });
    } catch (error) {
      if (error.statusCode) {
        return res.status(error.statusCode).json({
          error: error.message
        });
      }

      console.error('Add member error:', error);
      res.status(500).json({
        error: 'Internal server error',
        message: 'Failed to add member'
      });
    }
  }

  /**
   * Remove a member from a flat
   * DELETE /api/flats/:flatId/members/:userId
   */
  async removeMemberFromFlat(req, res) {
    try {
      const { flatId, userId: userIdToRemove } = req.params;
      const currentUserId = req.userId;

      // Check if current user is a member of the flat
      const isMember = await flatService.isUserMemberOfFlat(flatId, currentUserId);
      
      if (!isMember) {
        return res.status(403).json({
          error: 'Access denied',
          message: 'You are not a member of this flat'
        });
      }

      // Remove member
      await flatService.removeMemberFromFlat(flatId, userIdToRemove);

      res.status(200).json({
        message: 'Member removed successfully'
      });
    } catch (error) {
      if (error.statusCode) {
        return res.status(error.statusCode).json({
          error: error.message
        });
      }

      console.error('Remove member error:', error);
      res.status(500).json({
        error: 'Internal server error',
        message: 'Failed to remove member'
      });
    }
  }
}

export default new FlatController();
